#include <stdint.h>
#include <stdio.h>

#define UART0_DR        (*(volatile uint32_t *)0x4000C000u)
#define UART0_FR        (*(volatile uint32_t *)0x4000C018u)
#define UART0_FR_TXFF   (1u << 5)

void uart_putc(char c)
{
    while (UART0_FR & UART0_FR_TXFF) { }
    UART0_DR = (uint32_t)c;
}

/* 留给链接器，启动后自动调用 */
void SystemInit(void)
{
    /* 在真实板子上：配置时钟、Flash 等待状态、电源域。
     * 在 QEMU lm3s6965evb 上无需操作。 */
}

/* 一个 .data 变量演示初值确实从 Flash 搬到 SRAM */
static int counter = 42;

int main(void)
{
    printf("Hello via printf, value=%d\r\n", counter);
    printf("counter address = %p\r\n", (void *)&counter);
    while (1) { }
}
