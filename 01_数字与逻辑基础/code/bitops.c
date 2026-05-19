/*
 * 第 01 章 · 位运算演示
 *
 * 跑法：
 *     make run-bitops
 *
 * 这份程序演示嵌入式里最常用的位运算模式。
 * 看输出，对照 README §1.3。
 */

#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

/* 把无符号 32 位以二进制 + 十六进制打印 */
static void print_bin32(const char *label, uint32_t v)
{
    printf("%-22s = 0x%08" PRIx32 "  0b", label, v);
    for (int i = 31; i >= 0; --i) {
        putchar((v >> i) & 1u ? '1' : '0');
        if (i && i % 4 == 0) putchar('_');
    }
    putchar('\n');
}

/* --- 模拟一个 32 位寄存器，字段如下 ---
 *   bit  0      : EN     (使能)
 *   bit  5      : IRQ_EN (中断使能)
 *   bits 10..8  : PRESCALER (3 位分频系数)
 *   bits 23..16 : DATA     (8 位数据)
 */
#define EN_POS           0
#define EN_MSK           (1u << EN_POS)

#define IRQEN_POS        5
#define IRQEN_MSK        (1u << IRQEN_POS)

#define PRESCALER_POS    8
#define PRESCALER_MSK    (0x7u << PRESCALER_POS)

#define DATA_POS         16
#define DATA_MSK         (0xFFu << DATA_POS)

int main(void)
{
    puts("=== 一、最基本的 set / clear / toggle / test ===");
    uint32_t REG = 0;
    print_bin32("初值 REG", REG);

    REG |= (1u << 5);                              /* set   bit 5 */
    print_bin32("set bit 5", REG);

    REG |= (1u << 12);                             /* set   bit 12 */
    print_bin32("set bit 12", REG);

    REG ^= (1u << 5);                              /* toggle bit 5（变 0） */
    print_bin32("toggle bit 5", REG);

    REG &= ~(1u << 12);                            /* clear bit 12 */
    print_bin32("clear bit 12", REG);

    int b5 = (REG & (1u << 5)) ? 1 : 0;
    int b3 = (REG & (1u << 3)) ? 1 : 0;
    printf("test bit 5 = %d, bit 3 = %d\n\n", b5, b3);

    puts("=== 二、多位字段读写（典型外设寄存器场景） ===");
    REG = 0;
    REG |= EN_MSK;                                 /* 使能 */
    REG |= IRQEN_MSK;                              /* 打开中断 */
    /* 写 PRESCALER = 5 */
    REG = (REG & ~PRESCALER_MSK) | ((5u << PRESCALER_POS) & PRESCALER_MSK);
    /* 写 DATA = 0xA3 */
    REG = (REG & ~DATA_MSK)      | ((0xA3u << DATA_POS) & DATA_MSK);
    print_bin32("最终 REG", REG);

    uint32_t prescaler = (REG & PRESCALER_MSK) >> PRESCALER_POS;
    uint32_t data      = (REG & DATA_MSK)      >> DATA_POS;
    printf("读字段：PRESCALER=%" PRIu32 ", DATA=0x%02" PRIx32 "\n\n",
           prescaler, data);

    puts("=== 三、教科书技巧 ===");
    uint32_t x = 0xB4u;            /* = 0b1011_0100 */
    print_bin32("x", x);
    print_bin32("x & (x-1)  低位1清掉", x & (x - 1));
    print_bin32("x & -x     仅留最低1", x & (uint32_t)(-(int32_t)x));

    uint32_t pow2 = 0x40;
    uint32_t notp = 0x42;
    printf("0x40 是 2 的幂？ %s\n", ((pow2 & (pow2 - 1)) == 0) ? "是" : "否");
    printf("0x42 是 2 的幂？ %s\n", ((notp & (notp - 1)) == 0) ? "是" : "否");
    puts("");

    puts("=== 四、向上对齐（DMA 缓冲、外设地址常用） ===");
    #define ALIGN_UP(a, b)  (((a) + (b) - 1u) & ~((b) - 1u))
    printf("ALIGN_UP(13, 8)   = %u\n", ALIGN_UP(13u, 8u));
    printf("ALIGN_UP(0x1003, 0x100) = 0x%X\n", ALIGN_UP(0x1003u, 0x100u));
    puts("");

    puts("=== 五、大小端互换（写网络协议、读外部传感器经常用） ===");
    uint32_t be = 0x12345678u;     /* 比如来自网络字节序的数据 */
    uint32_t le = ((be & 0xFF000000u) >> 24) |
                  ((be & 0x00FF0000u) >>  8) |
                  ((be & 0x0000FF00u) <<  8) |
                  ((be & 0x000000FFu) << 24);
    printf("BE 0x%08" PRIx32 "  ->  LE 0x%08" PRIx32 "\n", be, le);
    /* GCC/Clang 也提供内建：__builtin_bswap32(be) */

    puts("");
    puts("=== 六、溢出与位宽 ===");
    uint8_t  u8  = 255;
    int8_t   i8  = 127;
    printf("(uint8_t)(255 + 1) = %u   (绕回 0)\n",         (unsigned)(uint8_t)(u8 + 1));
    printf("(int8_t)(127 + 1)  = %d   (有符号溢出 UB!)\n",
           (int)(int8_t)(i8 + 1));
    /* 有符号溢出在 C 里是 undefined behavior。
       嵌入式协议里一切计数器、序号字段都倾向用无符号类型。 */

    return 0;
}
