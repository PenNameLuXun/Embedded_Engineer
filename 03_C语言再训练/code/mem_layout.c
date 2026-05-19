/*
 * 打印各种变量的地址，直观看出 .text/.rodata/.data/.bss/stack/heap 分布。
 *
 * 跑法： make && ./mem_layout
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int      g_data_int  = 0xDEADBEEF;   /* .data */
int      g_bss_int;                  /* .bss */
const char g_rodata_str[] = "I live in .rodata";

static void some_function(void) { }

int main(void)
{
    int       local_int       = 1;             /* stack */
    static int s_data_int     = 0x55AA;        /* .data */
    static int s_bss_int;                      /* .bss */
    void *heap = malloc(64);                   /* heap */

    printf("=== 各段地址（典型 Linux x86_64，地址会随机化但相对位置稳定） ===\n");
    printf(".text  (函数代码)     main           = %p\n", (void *)main);
    printf(".text                  some_function  = %p\n", (void *)some_function);
    printf(".rodata (常量字符串)  g_rodata_str   = %p\n", (void *)g_rodata_str);
    printf(".data  (已初始化全局) g_data_int     = %p\n", (void *)&g_data_int);
    printf(".data  (函数 static)  s_data_int     = %p\n", (void *)&s_data_int);
    printf(".bss   (未初始化全局) g_bss_int      = %p\n", (void *)&g_bss_int);
    printf(".bss   (函数 static)  s_bss_int      = %p\n", (void *)&s_bss_int);
    printf("heap   (malloc)        heap           = %p\n", heap);
    printf("stack  (函数局部)      local_int      = %p\n", (void *)&local_int);

    free(heap);
    return 0;
}
