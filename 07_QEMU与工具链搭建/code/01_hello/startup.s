.syntax unified
.cpu cortex-m3
.thumb

/* 最小中断向量表：栈顶 + 复位向量 + 几个异常 */
.section .isr_vector, "a", %progbits
.word _estack
.word reset_handler
.word default_handler   /* NMI            */
.word default_handler   /* HardFault      */
.word default_handler   /* MemManage      */
.word default_handler   /* BusFault       */
.word default_handler   /* UsageFault     */
.word 0
.word 0
.word 0
.word 0
.word default_handler   /* SVCall         */
.word default_handler   /* DebugMonitor   */
.word 0
.word default_handler   /* PendSV         */
.word default_handler   /* SysTick        */

.section .text
.thumb_func
.global reset_handler
reset_handler:
    bl  main
    b   .

.thumb_func
.global default_handler
default_handler:
    b   .
