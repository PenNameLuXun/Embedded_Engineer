#include <stdint.h>
#include <stdio.h>
#include "mini_rtos.h"

/* UART (lm3s6965 PL011) */
#define UART0_DR    (*(volatile uint32_t *)0x4000C000u)
#define UART0_FR    (*(volatile uint32_t *)0x4000C018u)
#define SYSCTL_RCGC1 (*(volatile uint32_t *)0x400FE104u)
#define SYSCTL_RCGC2 (*(volatile uint32_t *)0x400FE108u)
#define GPIOA_DEN   (*(volatile uint32_t *)0x4000451Cu)
#define GPIOA_AFSEL (*(volatile uint32_t *)0x40004420u)
#define UART0_IBRD  (*(volatile uint32_t *)0x4000C024u)
#define UART0_FBRD  (*(volatile uint32_t *)0x4000C028u)
#define UART0_LCRH  (*(volatile uint32_t *)0x4000C02Cu)
#define UART0_CTL   (*(volatile uint32_t *)0x4000C030u)

void uart_init(void) {
    SYSCTL_RCGC1 |= 1u; SYSCTL_RCGC2 |= 1u;
    GPIOA_DEN |= 3u; GPIOA_AFSEL |= 3u;
    UART0_CTL &= ~1u;
    uint32_t brd = (50000000u * 4u) / 115200u;
    UART0_IBRD = brd / 64u; UART0_FBRD = brd & 0x3Fu;
    UART0_LCRH = (3u << 5) | (1u << 4);
    UART0_CTL  = 0x301u;
}
void uart0_putc(char c) {
    while (UART0_FR & (1u << 5)) {}
    UART0_DR = (uint32_t)c;
}

void SystemInit(void) {}

static uint32_t stack1[256], stack2[256], stack3[256];

static void task1(void *arg) {
    (void)arg;
    uint32_t n = 0;
    while (1) { printf("task1 #%lu\r\n", (unsigned long)++n); rtos_delay(300); }
}
static void task2(void *arg) {
    (void)arg;
    uint32_t n = 0;
    while (1) { printf("  task2 #%lu\r\n", (unsigned long)++n); rtos_delay(700); }
}
static void task3(void *arg) {
    (void)arg;
    uint32_t n = 0;
    while (1) { printf("    task3 #%lu\r\n", (unsigned long)++n); rtos_delay(1100); }
}

int main(void)
{
    uart_init();
    printf("=== mini_rtos demo ===\r\n");
    rtos_task_create(task1, "t1", stack1, 256, NULL);
    rtos_task_create(task2, "t2", stack2, 256, NULL);
    rtos_task_create(task3, "t3", stack3, 256, NULL);
    rtos_start();
    while (1) {}
}
