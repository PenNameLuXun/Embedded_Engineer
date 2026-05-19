/* 给 volatile_demo.c 提供外部定义，避免链接报错。
 * 我们不真的跑这俩函数，只看汇编。*/
#include <stdint.h>

volatile uint32_t v_flag  = 0;
uint32_t          nv_flag = 0;
