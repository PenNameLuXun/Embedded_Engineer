# 第 03 章自检题参考答案

1. `.rodata`（嵌入式上 = Flash），整个程序生命周期。

2.   
   (a) 是。32 位对齐写在 ARMv7-M 上单条 STR 指令完成，原子。  
   (b) 不是。Cortex-M3 没 64 位原生访问，会被编译成两条 STR，可被中断切开。  
   (c) 不是。`i++` = LDR / ADD / STR 三步。

3. `volatile int *p` —— 指向 volatile int 的指针（指向的对象 volatile）。  
   `int * volatile p` —— volatile 的指针（指针本身 volatile，指向的对象普通）。  
   前者用于外设寄存器；后者罕见，用于 ISR 可能改你的指针变量时。

4. 默认对齐：`sizeof = 6`（a + pad1 + b + c + pad1）。重排为 `b, a, c` 或 `b, c, a` 可以到 5 或 4 不等取决于编译器收尾对齐。

5. 总线/CPU 可能先把 CTRL 寄存器的 ENABLE 写出去，再写 LEN，DMA 看到 ENABLE 时 LEN 还是旧值，搬错数据量。`__DSB()` 强制按程序顺序对外设可见。
