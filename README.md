# 嵌入式工程师从零到深入

一本系统化的嵌入式学习教材，**45 章 + 路线图**，覆盖：

- **硬件基础**：数字逻辑、计算机体系结构、电子电路、时序
- **MCU 裸机**：Cortex-M、启动文件、链接脚本、GPIO/UART、中断、定时器、DMA、ADC
- **通信协议与 IP 核**：UART、SPI、I²C、CAN、USB、Ethernet、PCIe、MIPI、无线
- **RTOS**：概念与调度、mini-RTOS 实战、Zephyr、实时性深入
- **嵌入式 Linux**：启动流程、Buildroot、设备树、字符 / 子系统驱动、调试性能
- **SoC / FPGA**：Verilog、FSM、AXI/AHB/APB、SoC 集成、FPGA 验证
- **进阶专题**：安全、低功耗、OTA、边缘 AI、功能安全、Embedded Rust

## 教材组织

每章 = 一个目录：

```
NN_章节名/
├── README.md      ← 教材正文
└── code/          ← 可编译可运行的示例代码 + Makefile + answers.md
```

**全程跑在 QEMU 上**，不依赖物理硬件。

## 从哪里开始

👉 **[完整路线图与章节索引：ROADMAP.md](./ROADMAP.md)**

## 已在 QEMU 上实测的示例

| 章节 | 程序 | 内容 |
|------|------|------|
| 07 | `01_hello` | 最小裸机 + UART |
| 09 | `02_hello_upgraded` | newlib printf + 完整启动 |
| 10 | `03_echo` | UART echo + GPIO LED |
| 11 | `04_irq_echo` | UART RX 中断 + SPSC ring buffer |
| 12 | `05_pwm/tick_demo` | SysTick 1 ms 节拍 |
| 13 | `06_dma/mem_to_mem_demo` | DMA 描述符接口 |
| 25 | `07_mini_rtos` | ~250 行可抢占内核，三任务交错 |

平台：`qemu-system-arm -M lm3s6965evb` (Cortex-M3) / `mps2-an385` (Cortex-M3) / 通用 Linux `virt`。

## 必备工具

```bash
sudo apt-get install -y \
    gcc-arm-none-eabi libnewlib-arm-none-eabi \
    gcc qemu-system-arm gdb-multiarch \
    build-essential iverilog gtkwave
```

各章节会按需提示额外工具。

## 学习路径建议

- **顺读**：00 → 45，依赖关系递进
- **MCU 工程师快线**：00 → 02 → 03 → 07–14 → 24–25
- **Linux 嵌入式快线**：00 → 02 → 03 → 04 → 06 → 20 → 28–34
- **IC / FPGA 快线**：00 → 01 → 02 → 05 → 06 → 35–39

## License

MIT
