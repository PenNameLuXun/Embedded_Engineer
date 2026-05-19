# 第 25 章自检题答案

1. EXC_RETURN = 0xFFFFFFFD 的特殊编码告诉 CPU："这次异常返回要回到 **thread 模式 + 使用 PSP + base frame**"。我们伪造栈帧时是这种状态，所以 LR 必须填这个值。返回到普通函数（thread+MSP）用 0xFFFFFFF9；返回到 handler 用 0xFFFFFFF1。

2. PendSV 优先级最低 → 它一定在所有 ISR 跑完后才执行。**保证上下文切换发生在系统"安静"时刻**，不会在嵌套 ISR 中途切栈。在 SysTick 自己里直接切栈会和嵌套中断冲突，**这是 ARM 设计 PendSV 的原意**。

3. 经典反转场景：高优先级 task 等 mutex，低 task 持 mutex，中等优先级 task 不需要 mutex 但能抢占低 task → 低 task 不跑 → mutex 不释放 → 高 task 间接被中等挡住。本 mini_rtos 没有 mutex，但你后续加上时如果不实现优先级继承，多任务系统会"莫名卡顿"。

4. SysTick 越高，调度抖动越小但调度开销越大。1 kHz (1 ms tick) 是 FreeRTOS / Linux 默认，平均 0.5 ms 抖动 + 1% CPU 开销。10 kHz (100 µs tick) 抖动 50 µs + 5–10% 开销。**100 kHz 以上几乎所有 CPU 都耗在 SysTick ISR 里**，没意义。要更高分辨率应用通用定时器单独触发。
