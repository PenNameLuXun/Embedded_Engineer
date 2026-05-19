.syntax unified
.cpu cortex-m3
.thumb
.text

/* start_first_task：直接触发 SVC（此时还在 thread+MSP），
 * 由 SVC_Handler 完成 PSP 设置 + 切到 thread+PSP + 跳到首个 task。 */
.global start_first_task
.thumb_func
start_first_task:
    svc     #0
    b       .                   /* 实际上不会到这 */


.global SVC_Handler
.thumb_func
SVC_Handler:
    /* 在 handler 模式 + MSP，硬件帧已经压到 MSP。 */
    ldr     r1, =g_cur_tcb
    ldr     r1, [r1]
    ldr     r0, [r1]            /* r0 = tcb->sp (指向软件帧 R4-R11) */

    ldmia   r0!, {r4-r11}        /* pop 软件帧 */
    msr     psp, r0              /* PSP = task 硬件帧首地址 */

    movs    r1, #2
    msr     control, r1          /* CONTROL.SPSEL=1（切到 PSP），保持特权 */
    isb

    ldr     r0, =0xFFFFFFFD       /* EXC_RETURN: thread+PSP */
    bx      r0


.global PendSV_Handler
.thumb_func
PendSV_Handler:
    cpsid   i

    mrs     r0, psp
    stmdb   r0!, {r4-r11}

    ldr     r1, =g_cur_tcb
    ldr     r1, [r1]
    str     r0, [r1]

    ldr     r1, =g_next_tcb
    ldr     r1, [r1]
    ldr     r0, [r1]

    ldmia   r0!, {r4-r11}
    msr     psp, r0

    cpsie   i
    bx      lr
