/*
 * struct padding 与 packed 的差别。
 */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

struct A {
    uint8_t  a;
    uint32_t b;
    uint16_t c;
    uint8_t  d;
};

struct B {                /* 字段按大小降序：更紧 */
    uint32_t b;
    uint16_t c;
    uint8_t  a;
    uint8_t  d;
};

struct __attribute__((packed)) C {  /* 强制去 padding */
    uint8_t  a;
    uint32_t b;
    uint16_t c;
    uint8_t  d;
};

#define DUMP(T, F) printf("  " #F " @ offset %2zu\n", offsetof(T, F))

int main(void)
{
    printf("struct A (默认对齐，混乱顺序) sizeof = %zu\n", sizeof(struct A));
    DUMP(struct A, a); DUMP(struct A, b); DUMP(struct A, c); DUMP(struct A, d);

    printf("struct B (默认对齐，降序顺序) sizeof = %zu\n", sizeof(struct B));
    DUMP(struct B, b); DUMP(struct B, c); DUMP(struct B, a); DUMP(struct B, d);

    printf("struct C (packed，强制紧凑)    sizeof = %zu\n", sizeof(struct C));
    DUMP(struct C, a); DUMP(struct C, b); DUMP(struct C, c); DUMP(struct C, d);
    return 0;
}
