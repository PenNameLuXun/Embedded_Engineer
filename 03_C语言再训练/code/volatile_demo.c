/*
 * 用 -O2 编译，对比 volatile 和非 volatile 的汇编差异。
 *
 *     make show-volatile
 */
#include <stdint.h>

extern volatile uint32_t v_flag;
extern uint32_t          nv_flag;

/* 这两个函数等待 flag 变 1。
 * 编译 -O2 时：
 *   wait_v  会真的每次读内存
 *   wait_nv 会被优化成"读一次就死循环"
 */
void wait_v(void)  { while (v_flag == 0)  { } }
void wait_nv(void) { while (nv_flag == 0) { } }
