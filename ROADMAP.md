# 嵌入式工程师从零到深入 · 总路线图

> 这是一本面向"会写一点 C、玩过 Arduino / 树莓派，但没真正下到寄存器和总线层面"的学习者的系统教材。  
> 全程使用 **QEMU** 模拟，不依赖任何物理硬件。每章 = 一个目录 = 一篇 `README.md` 教材 + 一个 `code/` 子目录里可编译可运行的示例。

---

## 设计原则

1. **先建模型再讲细节**：每章先给"心智模型"（这玩意儿为什么存在、解决什么问题），再讲实现细节。
2. **协议讲到信号级**：不是"调一个 API 把字符串发出去"，而是"线上每一比特长什么样、谁在驱动这根线"。
3. **代码必须能跑**：所有示例都基于 QEMU + 开源工具链（`gcc-arm-none-eabi` / `riscv64-unknown-elf-gcc` / `iverilog` / `verilator` / `qemu-system-*`），Makefile 一键编译运行。
4. **层与层互相穿透**：硬件章会指向用到这硬件的软件章，软件章会回引硬件原理章，形成网络而不是流水线。

---

## 章节总览

### 第 0 部分　预备 · Foundations

| #  | 章节                       | 关键词                                         |
|----|----------------------------|------------------------------------------------|
| 00 | 导论：嵌入式到底是什么     | 嵌入式 vs 通用计算、约束、产业地图             |
| 01 | 数字与逻辑基础             | 二进制/十六进制、位运算、布尔代数、组合 vs 时序 |
| 02 | 计算机体系结构速通         | 冯·诺依曼/哈佛、ISA、寄存器、流水线、Cache     |
| 03 | C 语言再训练（嵌入式视角） | 指针/内存模型/`volatile`/链接/位域/对齐         |

### 第 1 部分　硬件入门 · Hardware

| #  | 章节                  | 关键词                                              |
|----|-----------------------|-----------------------------------------------------|
| 04 | 电子电路最小集        | 欧姆定律、电容/电感的"信号视角"、上拉/下拉/开漏     |
| 05 | 数字电路与时序        | 门、触发器、建立/保持时间、亚稳态、时钟域           |
| 06 | 总线与时序图          | 同步/异步、握手、读时序图的方法                    |

### 第 2 部分　MCU 裸机 · Bare-metal

| #  | 章节                       | 关键词                                                  |
|----|----------------------------|---------------------------------------------------------|
| 07 | QEMU 与工具链搭建          | `gcc-arm-none-eabi`、`qemu-system-arm`、GDB             |
| 08 | ARM Cortex-M 架构          | 模式、寄存器组、栈、异常模型、NVIC、MPU、内存映射       |
| 09 | 启动文件与链接脚本         | 复位向量、`.data/.bss` 初始化、链接段、`ld` 脚本        |
| 10 | 第一个程序：寄存器级 GPIO  | `mps2-an385` / `lm3s6965evb`，直写寄存器点 UART         |
| 11 | 中断与异常                 | 优先级、抢占、ISR 编写、临界区、中断延迟                |
| 12 | 定时器与 SysTick           | 节拍、PWM、输入捕获、多通道                              |
| 13 | DMA                        | 链表/循环模式、外设触发、对 CPU 的"卸载"                |
| 14 | ADC/DAC 与混合信号简介     | 采样定理、量化噪声、SAR/Σ-Δ                              |

### 第 3 部分　通信协议与 IP 核 · Protocols & IPs

每章都包含：**协议层** + **典型 IP 核内部结构**（FIFO、波特率发生器、状态机） + **QEMU 上的实例**。

| #  | 章节                        | 关键词                                                      |
|----|-----------------------------|-------------------------------------------------------------|
| 15 | UART                        | 帧结构、波特率、自动波特检测、FIFO、流控                    |
| 16 | SPI                         | CPOL/CPHA、菊花链、四线/三线、QSPI/OSPI                     |
| 17 | I²C / SMBus                 | 仲裁、时钟拉伸、重复起始、多主                              |
| 18 | CAN / CAN-FD                | 仲裁、帧格式、错误界定、汽车场景                            |
| 19 | USB 概览                    | 描述符、枚举、传输类型、HID/CDC                             |
| 20 | Ethernet + TCP/IP 速通      | PHY/MAC、MII/RMII、ARP、IP、TCP 状态机                       |
| 21 | PCIe 概念                   | TLP、Root Complex、BAR、MSI/MSI-X                            |
| 22 | MIPI CSI/DSI                | D-PHY、数据包、Lane                                          |
| 23 | 无线协议入门                | BLE GAP/GATT、Wi-Fi PHY 速览、LoRa                           |

### 第 4 部分　RTOS

| #  | 章节                    | 关键词                                              |
|----|-------------------------|-----------------------------------------------------|
| 24 | RTOS 概念与调度         | 抢占、优先级反转、信号量、消息队列                  |
| 25 | FreeRTOS 实战（QEMU）   | 移植要点、任务、Tick、临界区                        |
| 26 | Zephyr 上手             | 设备树、Kconfig、子系统                              |
| 27 | 实时性深入              | WCET、EDF/RMS、抖动来源分析                          |

### 第 5 部分　嵌入式 Linux

| #  | 章节                          | 关键词                                              |
|----|-------------------------------|-----------------------------------------------------|
| 28 | 启动流程                      | BootROM → U-Boot → Kernel → init                    |
| 29 | 交叉编译 / Buildroot          | 工具链、根文件系统、最小镜像                        |
| 30 | 设备树（Device Tree）         | DTS 语法、`compatible`、绑定                         |
| 31 | 字符设备驱动入门              | `file_operations`、ioctl                            |
| 32 | 子系统驱动模型                | platform driver、GPIO/I2C/SPI 子系统                |
| 33 | 用户态接口                    | sysfs、procfs、netlink、UIO                          |
| 34 | 调试与性能                    | `ftrace`、`perf`、`kgdb`、`crash`                    |

### 第 6 部分　SoC / FPGA / 自己造一颗芯

| #  | 章节                        | 关键词                                              |
|----|-----------------------------|-----------------------------------------------------|
| 35 | Verilog 入门（仿真先行）    | iverilog、testbench、波形                            |
| 36 | 可综合 Verilog 与 FSM       | always 块陷阱、阻塞/非阻塞、Mealy/Moore              |
| 37 | 片上总线 AXI / AHB / APB    | 握手、突发、互连                                    |
| 38 | 集成软核 SoC                | PicoRV32 / Cortex-M0 DesignStart 概念               |
| 39 | FPGA 验证流程               | 仿真 → 综合 → 实现 → 时序收敛                       |

### 第 7 部分　进阶专题

| #  | 章节                  | 关键词                                                  |
|----|-----------------------|---------------------------------------------------------|
| 40 | 嵌入式安全            | Secure Boot、TrustZone、密码加速器、侧信道              |
| 41 | 低功耗设计            | 时钟门控、电源域、DVFS、唤醒源                          |
| 42 | OTA 与固件升级        | A/B 分区、差分升级、回滚                                |
| 43 | 边缘 AI               | TFLite Micro、量化、算子优化                            |
| 44 | 功能安全与编码规范    | ISO 26262、IEC 61508、MISRA-C                           |
| 45 | Embedded Rust         | `no_std`、HAL、所有权与 ISR                              |

---

## 学习路径建议

如果你要 **顺着读**，按 00 → 45 即可，依赖关系从前向后递进。  
如果你想 **抓重点**，可以走两条快线：

- **MCU 工程师快线**：00 → 02 → 03 → 07 → 08 → 09 → 10 → 11 → 12 → 15 → 16 → 17 → 24 → 25  
- **Linux 嵌入式快线**：00 → 02 → 03 → 04 → 06 → 20 → 28 → 29 → 30 → 31 → 32 → 33 → 34  
- **IC / FPGA 偏硬件快线**：00 → 01 → 02 → 05 → 06 → 35 → 36 → 37 → 38 → 39

---

## 工具链总清单

| 类别            | 工具                                          |
|-----------------|-----------------------------------------------|
| ARM 交叉编译    | `gcc-arm-none-eabi`                           |
| RISC-V 交叉编译 | `gcc-riscv64-unknown-elf` / `gcc-riscv64-linux-gnu` |
| 模拟器          | `qemu-system-arm`、`qemu-system-aarch64`、`qemu-system-riscv32/64` |
| 调试            | `gdb-multiarch`                                |
| 构建            | `make`、`cmake`、`ninja`                       |
| Verilog 仿真    | `iverilog` + `gtkwave`、`verilator`            |
| 嵌入式 Linux    | `buildroot`、`u-boot`、`linux`                 |
| RTOS            | `freertos-kernel`、`zephyrproject`             |

第 07 章会给出 Debian/Ubuntu 上一条命令装齐的方法。

---

## 进度

- [x] 路线图
- [x] **Part 0 预备**：00 导论、01 数字与逻辑、02 体系结构、03 C 再训练
- [x] **Part 1 硬件入门**：04 电子电路、05 数字电路与时序、06 总线与时序图
- [x] **Part 2 MCU 裸机**：07 QEMU+工具链、08 Cortex-M、09 启动+链接、10 GPIO/UART、11 中断、12 定时器、13 DMA、14 ADC
- [x] **Part 3 通信协议与 IP 核**：15 UART、16 SPI、17 I²C、18 CAN/CAN-FD、19 USB、20 Ethernet+TCP/IP、21 PCIe、22 MIPI CSI/DSI、23 无线
- [x] **Part 4 RTOS**：24 概念、25 mini-RTOS 实战、26 Zephyr、27 实时性深入
- [x] **Part 5 嵌入式 Linux**：28 启动、29 Buildroot、30 设备树、31 字符驱动、32 子系统驱动、33 用户态接口、34 调试与性能
- [x] **Part 6 SoC / FPGA**：35 Verilog、36 FSM、37 片上总线、38 SoC 集成、39 FPGA 验证
- [x] **Part 7 进阶专题**：40 安全、41 低功耗、42 OTA、43 边缘 AI、44 功能安全、45 Embedded Rust

**全教材 45 章 + ROADMAP 全部完成**。

**在 QEMU lm3s6965evb 上已验证可跑的示例**：
- `07_QEMU与工具链搭建/code/01_hello/` — 最小裸机 Hello
- `09_启动文件与链接脚本/code/02_hello_upgraded/` — printf via newlib + .data 拷贝
- `10_第一个程序_GPIO/code/03_echo/` — UART echo + LED
- `11_中断与异常/code/04_irq_echo/` — UART RX 中断 + ring buffer
- `12_定时器与SysTick/code/05_pwm/` — SysTick 1ms 节拍
- `13_DMA/code/06_dma/mem_to_mem_demo.c` — DMA 接口模型
- `25_FreeRTOS实战/code/07_mini_rtos/` — ~250 行可抢占内核（PendSV + PSP + SVC），三任务在 QEMU 上按 300/700/1100 ms 周期交错运行

**纯 Linux 主机上已验证的代码示例**：
- `01_数字与逻辑基础/code/bitops.c` — C 位运算
- `03_C语言再训练/code/{mem_layout,struct_pad,atomic_race}.c` — 内存布局 / 对齐 / lost update
