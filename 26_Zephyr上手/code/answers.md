# 第 26 章自检题答案

1. 三个原因：(a) 设备树已是工业标准，工程师上手成本低；(b) 同一份 DTS 既能给 Linux 又能给 Zephyr 用 (heterogeneous SoC 上方便)；(c) DT 强制硬件信息和代码解耦，正好对应 Zephyr "驱动可移植"的核心目标。

2. **K_THREAD_DEFINE**：编译期静态分配 TCB + 栈 + 队列槽位。**ROM 友好、零运行时分配**，启动时立刻 ready 跑。  
   **k_thread_create**：运行时动态创建，参数从内存池来。灵活但有失败可能 (内存不足)。  
   严肃产品默认用 `K_THREAD_DEFINE`，符合"避免动态分配"的嵌入式军规。

3. `DEVICE_DT_GET` 现代。前者按字符串查（运行时），后者按 DT 节点（编译期）。后者**类型安全 + 链接器丢弃未使用的 device 表，省 Flash**。新项目应一律用后者，老 Zephyr 代码逐步迁移。

4. 不现实。8051 (Harvard、64 KB code + 256 B internal RAM、无堆栈管理硬件) 跑不动 Zephyr 内核。**Zephyr 起步 32 位 + 至少 32 KB SRAM**。8 位 MCU 留给 FreeRTOS-MSP430、RT-Thread Nano 这类更小的 RTOS。
