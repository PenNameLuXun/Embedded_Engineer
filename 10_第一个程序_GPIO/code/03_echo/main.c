#include <stdio.h>
#include "uart.h"
#include "led.h"

int main(void)
{
    led_init();
    uart0_init(50000000u, 115200u);
    printf("== echo demo == 输入字符会回显，每 8 个字符切换 LED\r\n");

    int led = 0;
    int n   = 0;
    while (1) {
        if (uart0_rx_ready()) {
            char c = uart0_getc();
            uart0_putc(c);
            if (c == '\r') uart0_putc('\n');
            if (++n % 8 == 0) {
                led ^= 1;
                led_set(led);
                printf("\r\n[LED toggled to %d]\r\n", led);
            }
        }
    }
}
