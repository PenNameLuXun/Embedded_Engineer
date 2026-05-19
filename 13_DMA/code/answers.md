# 第 13 章自检题答案

1. **DMA 占用更低**。中断每字节都打断 CPU，进栈出栈 + 用户 ISR 代码大约 30–50 cycle / byte。1 Mbit/s 流量下 = ~100 K interrupt/s × 50 cycle = 5 MCPS 开销，50 MHz CPU 利用率 10%。DMA 每搬到目标 count 才中断一次，开销摊到几百字节一次 → 利用率 < 0.1%。

2. 三类常见原因：  
   (a) 没写 `__DSB()`，DMA 看到的描述符是"还没全更新"的状态；  
   (b) M7/A 系列 D-Cache 没 Clean，DRAM 里还是旧数据；  
   (c) buffer 在栈上，函数返回后被覆盖。

3. 源地址不变 = "从外设的同一个寄存器一直读"。典型场景：UART RX、ADC 结果寄存器、SPI 接收。

4. M0/M3/M4 没 D-Cache，CPU 与 DMA 看的是同一份内存视图。但仍要 `__DSB()` 保证 CPU 写已经"走到"内存（系统总线层面），尤其是 SoC 总线带 write-buffer 时。
