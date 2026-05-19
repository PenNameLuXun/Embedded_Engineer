/*
 * 用 pthread 在 PC 上重现 `counter++` 的 lost-update。
 *
 * 跑法： make && ./atomic_race
 *
 * 预期输出：non_atomic 远小于 200000；atomic 严格等于 200000。
 */
#include <stdio.h>
#include <stdint.h>
#include <stdatomic.h>
#include <pthread.h>

#define LOOPS    2000000
#define THREADS  4

static uint32_t           non_atomic = 0;
static atomic_uint        atom       = 0;

static void *worker_non(void *arg) {
    (void)arg;
    for (int i = 0; i < LOOPS; i++) non_atomic++;   /* 非原子，会丢更新 */
    return NULL;
}

static void *worker_atom(void *arg) {
    (void)arg;
    for (int i = 0; i < LOOPS; i++) atomic_fetch_add(&atom, 1);
    return NULL;
}

int main(void)
{
    pthread_t t[THREADS];

    for (int i = 0; i < THREADS; i++) pthread_create(&t[i], NULL, worker_non, NULL);
    for (int i = 0; i < THREADS; i++) pthread_join(t[i], NULL);

    for (int i = 0; i < THREADS; i++) pthread_create(&t[i], NULL, worker_atom, NULL);
    for (int i = 0; i < THREADS; i++) pthread_join(t[i], NULL);

    printf("期望: %d\n", LOOPS * THREADS);
    printf("non_atomic = %u   (注意：通常远小于期望，丢失更新)\n", non_atomic);
    printf("atomic     = %u   (严格等于期望)\n",
           (unsigned)atomic_load(&atom));
    return 0;
}
