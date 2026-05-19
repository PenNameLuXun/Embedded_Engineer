#include <stdint.h>
#include <stdio.h>
#include "regs.h"

/* ---- UART ---- */
static void uart0_init(uint32_t bus_clk_hz, uint32_t baud)
{
    SYSCTL_RCGC1 |= RCGC1_UART0;
    SYSCTL_RCGC2 |= RCGC2_GPIOA;
    GPIOA_DEN    |= 0x3u;
    GPIOA_AFSEL  |= 0x3u;
    UART0_CTL    &= ~UART0_CTL_UARTEN;
    uint32_t brd_x64 = (bus_clk_hz * 4u) / baud;
    UART0_IBRD = brd_x64 / 64u;
    UART0_FBRD = brd_x64 & 0x3Fu;
    UART0_LCRH = UART0_LCRH_WLEN_8 | UART0_LCRH_FEN;
    UART0_CTL  = UART0_CTL_UARTEN | UART0_CTL_TXE | UART0_CTL_RXE;
}

void uart0_putc(char c)
{
    while (UART0_FR & UART0_FR_TXFF) { }
    UART0_DR = (uint32_t)c;
}

/* ---- LED ---- */
static void led_init(void)
{
    SYSCTL_RCGC2 |= RCGC2_GPIOF;
    GPIOF_DIR    |= (1u << 0);
    GPIOF_DEN    |= (1u << 0);
}
static void led_set(int on)
{
    if (on) GPIOF_DATA |=  (1u << 0);
    else    GPIOF_DATA &= ~(1u << 0);
}

/* ---- NVIC helper ---- */
static void nvic_enable(int irq, int prio)
{
    *((volatile uint8_t *)(NVIC_IP_BASE + irq)) = (uint8_t)(prio << 5);
    NVIC_ISER0 = (1u << irq);
}

/* ---- ring buffer (SPSC) ---- */
#define RX_BUF_SZ 64
static volatile uint8_t  rx_buf[RX_BUF_SZ];
static volatile uint32_t rx_head = 0, rx_tail = 0;
static volatile uint32_t rx_drops = 0;

/* ---- ISR ---- */
void UART0_IRQHandler(void)
{
    UART0_ICR = UART0_ICR_RXIC;
    while ((UART0_FR & UART0_FR_RXFE) == 0) {
        uint8_t c = (uint8_t)(UART0_DR & 0xFFu);
        uint32_t next = (rx_head + 1u) % RX_BUF_SZ;
        if (next != rx_tail) {
            rx_buf[rx_head] = c;
            rx_head = next;
        } else {
            rx_drops++;
        }
    }
}

/* ---- main ---- */
void SystemInit(void) { }

int main(void)
{
    led_init();
    uart0_init(50000000u, 115200u);
    UART0_IM |= UART0_IM_RXIM;
    nvic_enable(UART0_IRQ_NUM, 2);
    __asm__("cpsie i");              /* __enable_irq */

    printf("== IRQ echo == 输入字符触发 ISR；每 8 字符切换 LED\r\n");

    int led = 0, n = 0;
    while (1) {
        if (rx_tail == rx_head) {
            __asm__("wfi");          /* 等中断把我叫醒 */
            continue;
        }
        uint8_t c = rx_buf[rx_tail];
        rx_tail = (rx_tail + 1u) % RX_BUF_SZ;
        uart0_putc((char)c);
        if (c == '\r') uart0_putc('\n');
        if (++n % 8 == 0) {
            led ^= 1; led_set(led);
            printf("\r\n[LED=%d drops=%lu]\r\n", led, (unsigned long)rx_drops);
        }
    }
}
