#pragma once
#include <stdint.h>

void uart0_init(uint32_t bus_clk_hz, uint32_t baud);
void uart0_putc(char c);
int  uart0_rx_ready(void);
char uart0_getc(void);
