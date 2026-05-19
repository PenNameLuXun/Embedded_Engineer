#include <stdint.h>

#define UART0_DR        (*(volatile uint32_t *)0x4000C000u)
#define UART0_FR        (*(volatile uint32_t *)0x4000C018u)
#define UART0_FR_TXFF   (1u << 5)

static void uart_putc(char c)
{
    while (UART0_FR & UART0_FR_TXFF) { }
    UART0_DR = (uint32_t)c;
}

static void uart_puts(const char *s)
{
    while (*s) uart_putc(*s++);
}

int main(void)
{
    uart_puts("Hello, embedded world!\r\n");
    while (1) { }
    return 0;
}

