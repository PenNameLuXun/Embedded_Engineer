#include "mini_rtos.h"

#define MAX_TASKS  8
static tcb_t  tcbs[MAX_TASKS];
static int    num_tasks = 0;
static int    cur_task  = 0;
static uint32_t idle_stack[64];

static void idle_task(void *arg) { (void)arg; while (1) __asm__ volatile("wfi"); }

tcb_t *g_cur_tcb;
tcb_t *g_next_tcb;

#define SYST_LOAD  (*(volatile uint32_t *)0xE000E014u)
#define SYST_VAL   (*(volatile uint32_t *)0xE000E018u)
#define SYST_CTRL  (*(volatile uint32_t *)0xE000E010u)
#define SCB_ICSR   (*(volatile uint32_t *)0xE000ED04u)
#define SCB_SHPR3  (*(volatile uint32_t *)0xE000ED20u)
#define ICSR_PENDSVSET   (1u << 28)

extern void start_first_task(uint32_t *sp);

void rtos_task_create(void (*fn)(void *), const char *name,
                      uint32_t *stack, int stack_words, void *arg)
{
    tcb_t *t = &tcbs[num_tasks++];
    t->name = name;
    t->state = TS_READY;
    t->delay_ticks = 0;

    uint32_t *sp = stack + stack_words;
    /* 硬件帧 */
    *(--sp) = 0x01000000u;          /* xPSR (T bit) */
    *(--sp) = (uint32_t)fn;         /* PC */
    *(--sp) = 0xFFFFFFFDu;          /* LR = EXC_RETURN thread+PSP */
    *(--sp) = 12;                   /* R12 */
    *(--sp) = 3; *(--sp) = 2; *(--sp) = 1;
    *(--sp) = (uint32_t)arg;        /* R0 */
    /* 软件帧 R4-R11 */
    for (int i = 11; i >= 4; i--) *(--sp) = (uint32_t)i;

    t->sp = sp;
}

static int pick_next(void);

void rtos_delay(uint32_t ms)
{
    __asm__ volatile("cpsid i");
    tcbs[cur_task].delay_ticks = ms;
    tcbs[cur_task].state       = TS_BLOCKED;
    int next = pick_next();
    g_cur_tcb  = &tcbs[cur_task];
    g_next_tcb = &tcbs[next];
    cur_task   = next;
    SCB_ICSR = ICSR_PENDSVSET;
    __asm__ volatile("cpsie i");
    /* PendSV 立刻接管，切到下一 task。
     * 我们这个 task 唤醒时从 PendSV 返回，回到这里之后 ret。 */
}

static int pick_next(void)
{
    /* idle task 永远是最后一个，永远 READY，所以一定有 task 能跑 */
    for (int i = 1; i <= num_tasks; i++) {
        int n = (cur_task + i) % num_tasks;
        if (tcbs[n].state == TS_READY) return n;
    }
    /* 不会到这 */
    return num_tasks - 1;
}

void SysTick_Handler(void)
{
    for (int i = 0; i < num_tasks; i++) {
        if (tcbs[i].state == TS_BLOCKED && tcbs[i].delay_ticks) {
            if (--tcbs[i].delay_ticks == 0)
                tcbs[i].state = TS_READY;
        }
    }
    int next = pick_next();
    if (next != cur_task) {
        g_cur_tcb  = &tcbs[cur_task];
        g_next_tcb = &tcbs[next];
        cur_task   = next;
        SCB_ICSR   = ICSR_PENDSVSET;
    }
}

void rtos_start(void)
{
    /* 注入 idle task 作为最后一个 task —— 所有别人都 blocked 时它跑 */
    rtos_task_create(idle_task, "idle", idle_stack, 64, 0);

    SYST_LOAD = (50000000u / 1000u) - 1u;
    SYST_VAL  = 0;

    /* PendSV 优先级 0xFF（最低） */
    SCB_SHPR3 = (SCB_SHPR3 & 0xFF00FFFFu) | (0xFFu << 16);

    cur_task   = 0;
    g_cur_tcb  = &tcbs[0];
    g_next_tcb = &tcbs[0];

    SYST_CTRL = 0x7;   /* 启 SysTick */
    start_first_task(tcbs[0].sp);
}
