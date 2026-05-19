#pragma once
#include <stdint.h>

typedef enum { TS_READY, TS_BLOCKED } task_state_t;

typedef struct {
    uint32_t   *sp;
    task_state_t state;
    uint32_t    delay_ticks;
    const char *name;
} tcb_t;

void rtos_task_create(void (*fn)(void *), const char *name,
                      uint32_t *stack, int stack_words, void *arg);
void rtos_delay(uint32_t ms);
void rtos_start(void);
