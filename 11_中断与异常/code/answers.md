# 第 11 章自检题答案

1. Cortex-M 进入异常时硬件自动 stacking R0–R3、R12、LR、PC、xPSR；R4–R11 由编译器在 ISR 前序 push 进栈。返回时硬件 + 编译器反向操作。整套被 ABI 兼容地处理，所以 C 函数能直接当 ISR。

2. (a) 外设本身的中断使能位（如 UART_IM）；(b) NVIC 里这个 IRQn 是否被 ISER 使能；(c) CPU 全局 PRIMASK 是否清零 (`__enable_irq`)。

3. 多半是没在 ISR 里清外设的中断标志（IFG/ICR）。退出 ISR 时 CPU 看 IRQ 线还高，立刻又进入。

4. 单生产者单消费者 + 指针自身原子写（对齐 32 位） + 严格顺序"先写数据再更新指针"。一旦多生产者或多消费者，需要锁 / LDREX/STREX。

5. `__disable_irq` 关所有可屏蔽中断（除 NMI/HardFault），简单粗暴；`BASEPRI` 只关优先级 ≥ N 的，比 N 更紧急的还能进。RTOS 临界区用 BASEPRI 保证高优先级中断仍能响应（如 FreeRTOS 的 `configMAX_SYSCALL_INTERRUPT_PRIORITY`）。
