/*
 * 概念演示：把"DMA 描述符 + 启动 + 完成回调"的接口画一遍。
 * 真实搬运用纯软件做（QEMU 上没法真跑硬件 µDMA），
 * 但调用模式与硬件 DMA 一致，便于建立心智模型。
 *
 * 跑法： make TARGET=mem_to_mem_demo run
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern void uart0_putc(char c);

typedef enum {
    DMA_WIDTH_8  = 1,
    DMA_WIDTH_16 = 2,
    DMA_WIDTH_32 = 4,
} dma_width_t;

typedef struct {
    void       *src;
    void       *dst;
    int         src_inc;
    int         dst_inc;
    dma_width_t width;
    uint32_t    count;
    void      (*on_done)(void);
} dma_desc_t;

/* 模拟的 DMA 引擎：在真硬件上这是几条寄存器写。 */
static void dma_start(const dma_desc_t *d)
{
    uint8_t *s = (uint8_t *)d->src;
    uint8_t *t = (uint8_t *)d->dst;
    for (uint32_t i = 0; i < d->count; i++) {
        memcpy(t, s, d->width);
        if (d->src_inc) s += d->width;
        if (d->dst_inc) t += d->width;
    }
    /* "DMA 完成中断" 在真硬件上由 NVIC 触发，这里直接同步回调。 */
    if (d->on_done) d->on_done();
}

static volatile int g_done;

static void on_done(void) { g_done = 1; }

void SystemInit(void) { }

extern void uart_init_lazy(void);  /* 仅给 printf 用 */

int main(void)
{
    extern void uart_init_for_demo(void);
    uart_init_for_demo();
    printf("=== DMA 概念演示 ===\r\n");

    static const char src[] = "Hello via fake DMA!\r\n";
    static       char dst[sizeof(src)];

    dma_desc_t d = {
        .src     = (void *)src,
        .dst     = dst,
        .src_inc = 1,
        .dst_inc = 1,
        .width   = DMA_WIDTH_8,
        .count   = sizeof(src),
        .on_done = on_done,
    };

    g_done = 0;
    dma_start(&d);
    while (!g_done) { }
    printf("DMA done, dst = %s", dst);

    while (1) { __asm__("wfi"); }
}

/* 简易 UART 初始化（与 ch10 一致），重复代码以便单文件演示 */
#define SYSCTL_RCGC1   (*(volatile uint32_t *)0x400FE104u)
#define SYSCTL_RCGC2   (*(volatile uint32_t *)0x400FE108u)
#define GPIOA_DEN      (*(volatile uint32_t *)0x4000451Cu)
#define GPIOA_AFSEL    (*(volatile uint32_t *)0x40004420u)
#define UART0_DR       (*(volatile uint32_t *)0x4000C000u)
#define UART0_FR       (*(volatile uint32_t *)0x4000C018u)
#define UART0_IBRD     (*(volatile uint32_t *)0x4000C024u)
#define UART0_FBRD     (*(volatile uint32_t *)0x4000C028u)
#define UART0_LCRH     (*(volatile uint32_t *)0x4000C02Cu)
#define UART0_CTL      (*(volatile uint32_t *)0x4000C030u)

void uart_init_for_demo(void)
{
    SYSCTL_RCGC1 |= 1u; SYSCTL_RCGC2 |= 1u;
    GPIOA_DEN |= 3u; GPIOA_AFSEL |= 3u;
    UART0_CTL &= ~1u;
    uint32_t brd = (50000000u * 4u) / 115200u;
    UART0_IBRD = brd / 64u;
    UART0_FBRD = brd & 0x3F;
    UART0_LCRH = (3u<<5) | (1u<<4);
    UART0_CTL  = 0x301u;
}

void uart0_putc(char c)
{
    while (UART0_FR & (1u<<5)) {}
    UART0_DR = (uint32_t)c;
}
