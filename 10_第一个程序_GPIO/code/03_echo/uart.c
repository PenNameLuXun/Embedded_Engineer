#include "uart.h"
#include "regs.h"

void uart0_init(uint32_t bus_clk_hz, uint32_t baud)
{
    SYSCTL_RCGC1 |= RCGC1_UART0;
    SYSCTL_RCGC2 |= RCGC2_GPIOA;

    GPIOA_DEN   |= (1u << 0) | (1u << 1);
    GPIOA_AFSEL |= (1u << 0) | (1u << 1);

    UART0_CTL &= ~UART0_CTL_UARTEN;

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

int uart0_rx_ready(void)
{
    return (UART0_FR & UART0_FR_RXFE) == 0;
}

char uart0_getc(void)
{
    while (!uart0_rx_ready()) { }
    return (char)(UART0_DR & 0xFFu);
}
