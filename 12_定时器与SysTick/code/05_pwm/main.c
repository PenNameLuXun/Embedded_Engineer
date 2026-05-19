#include <stdint.h>
#include <stdio.h>

#define SYSCTL_RCGC1   (*(volatile uint32_t *)0x400FE104u)
#define SYSCTL_RCGC2   (*(volatile uint32_t *)0x400FE108u)
#define RCGC1_UART0    (1u << 0)
#define RCGC2_GPIOA    (1u << 0)

#define GPIOA_DEN      (*(volatile uint32_t *)0x4000451Cu)
#define GPIOA_AFSEL    (*(volatile uint32_t *)0x40004420u)

#define UART0_DR       (*(volatile uint32_t *)0x4000C000u)
#define UART0_FR       (*(volatile uint32_t *)0x4000C018u)
#define UART0_IBRD     (*(volatile uint32_t *)0x4000C024u)
#define UART0_FBRD     (*(volatile uint32_t *)0x4000C028u)
#define UART0_LCRH     (*(volatile uint32_t *)0x4000C02Cu)
#define UART0_CTL      (*(volatile uint32_t *)0x4000C030u)

#define SYST_CTRL  (*(volatile uint32_t *)0xE000E010u)
#define SYST_LOAD  (*(volatile uint32_t *)0xE000E014u)
#define SYST_VAL   (*(volatile uint32_t *)0xE000E018u)

#define CPU_HZ  50000000u

static void uart_init(void)
{
    SYSCTL_RCGC1 |= RCGC1_UART0;
    SYSCTL_RCGC2 |= RCGC2_GPIOA;
    GPIOA_DEN    |= 0x3u;
    GPIOA_AFSEL  |= 0x3u;
    UART0_CTL    &= ~1u;
    uint32_t brd_x64 = (CPU_HZ * 4u) / 115200u;
    UART0_IBRD = brd_x64 / 64u;
    UART0_FBRD = brd_x64 & 0x3Fu;
    UART0_LCRH = (3u << 5) | (1u << 4);
    UART0_CTL  = (1u << 0) | (1u << 8) | (1u << 9);
}

void uart0_putc(char c)
{
    while (UART0_FR & (1u << 5)) { }
    UART0_DR = (uint32_t)c;
}

static volatile uint32_t g_ticks;

void SysTick_Handler(void) { g_ticks++; }

static void systick_init_1ms(void)
{
    SYST_LOAD = (CPU_HZ / 1000u) - 1u;
    SYST_VAL  = 0;
    SYST_CTRL = 0x7;
}

static void delay_ms(uint32_t ms)
{
    uint32_t start = g_ticks;
    while ((g_ticks - start) < ms) { __asm__("wfi"); }
}

void SystemInit(void) { }

int main(void)
{
    uart_init();
    systick_init_1ms();
    __asm__("cpsie i");

    printf("SysTick tick demo. Loop: print every 500 ms.\r\n");
    for (uint32_t i = 0;; i++) {
        delay_ms(500);
        printf("[%lu] ticks = %lu\r\n",
               (unsigned long)i, (unsigned long)g_ticks);
    }
}
