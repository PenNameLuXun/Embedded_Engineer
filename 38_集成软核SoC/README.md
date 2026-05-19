# 第 38 章　集成软核 SoC：自己造一颗芯

> 把 CPU、内存、外设 + 总线放一起 = 一个 SoC。开源软核（PicoRV32、CV32E40P、Ibex、Cortex-M0 DesignStart）让你在 FPGA 上"造一颗"芯片。这一章教你 SoC 集成的基本思路。
>
> **学完本章你应该能**：(1) 解释 hard core vs soft core，(2) 知道几个主流开源软核，(3) 看到 SoC 框图能画出 AXI/AHB/APB 分层，(4) 大致知道 FPGA 上跑一个 RISC-V SoC 的流程。

---

## 38.1 Soft Core vs Hard Core

| 类型      | 在哪                             | 例子                              |
|-----------|----------------------------------|-----------------------------------|
| Hard core | 芯片硅片上固化的 CPU             | Cortex-A53 在 RK3399 里、Apple M2 |
| Soft core | 一份 RTL 代码，烧到 FPGA 跑      | PicoRV32 在 FPGA 里                |

软核优点：随时改、跑在 FPGA 验证、定制指令集。  
缺点：跑得慢（50–150 MHz vs 硬核 GHz）、面积大、功耗高。

**研究 / 验证用软核，量产用硬核**。

---

## 38.2 主流开源软核

| 软核           | ISA         | 大小       | 特点                          |
|----------------|-------------|------------|-------------------------------|
| PicoRV32       | RV32I/M/C   | ~750 LUT   | 极小，单周期或多周期可选       |
| Ibex (zero-riscy) | RV32IM   | ~2K LUT    | lowRISC 项目，工业化            |
| CV32E40P       | RV32IMFC + 自定义扩展 | ~8K LUT  | OpenHW Group，类 ARM 风格        |
| VexRiscv       | RV32IM + Cache + MMU | ~5K LUT  | 可配置，运行 Linux              |
| Cortex-M0 DesignStart | ARMv6-M | ~5K LUT  | ARM 免费授权，能 license 量产    |
| NEORV32        | RV32 + 大量外设  | 10K LUT 起 | 自带 UART/SPI/I2C/PWM，一站式  |

新人选：**PicoRV32 学原理，NEORV32 学集成**。

---

## 38.3 一个最小 SoC 框图

```
      ┌──────────────────────────────────────────┐
      │                                            │
      │   ┌──────────────┐         ┌────────────┐ │
      │   │ PicoRV32 CPU │ ─ AXI ─→│ Memory     │ │
      │   │  (RV32I)     │         │ (BRAM 32K) │ │
      │   └──────────────┘         └────────────┘ │
      │          │                                 │
      │          └─ AXI-to-APB Bridge              │
      │                  │                         │
      │          ┌───────┴───────┬────────┐        │
      │          ↓               ↓        ↓        │
      │       ┌──────┐    ┌──────┐  ┌──────┐      │
      │       │ UART │    │ GPIO │  │ Timer│      │
      │       └──────┘    └──────┘  └──────┘      │
      │                                            │
      └────────────────────────────────────────────┘
            ↑           ↑           ↑
        RX/TX pins   board LEDs   (内部使用)
```

完整源码 ~3000 行 Verilog。**FPGA 一编译，你就拥有一颗自己造的 SoC**。

---

## 38.4 工具链怎么跑

```
1. 写 RTL (CPU + 总线 + 外设)
2. 仿真 (iverilog / Verilator)
3. 综合 (Vivado / Quartus / yosys)
4. 布局布线 (Vivado / nextpnr)
5. 生成 bitstream
6. 下载到 FPGA
7. 软件交叉编译 (riscv32-unknown-elf-gcc)
8. JTAG / UART 烧到 SoC 的 BRAM
9. 跑！
```

开源全套：**yosys + nextpnr + iverilog + Verilator + riscv-gnu-toolchain**。  
ICE40 / ECP5 等小 FPGA 完全用开源走通。Xilinx / Intel 需要厂家工具（Vivado / Quartus）。

---

## 38.5 异构多核 SoC

现代车载 / 工业 SoC 不止一颗 CPU：

```
   ┌─────────────────────────────────────────────┐
   │                                              │
   │   Cortex-A78 ×4  ──── 跑 Linux               │
   │      ↑                                       │
   │      │ Cache Coherent Interconnect          │
   │      ↓                                       │
   │   Cortex-R52 ×2  ──── 跑 Hypervisor + RTOS   │
   │      ↑                                       │
   │      │                                       │
   │   Cortex-M7      ──── 跑 安全岛 / 实时控制   │
   │                                              │
   │   AI 加速器 + GPU + ISP + NPU                │
   └─────────────────────────────────────────────┘
```

不同 CPU 域各自擅长：
- Cortex-A 系列：Linux + GUI + 网络
- Cortex-R 系列：硬实时 + ECC
- Cortex-M 系列：低功耗 + 安全监视器

**核间通信**靠共享内存 + 邮箱寄存器 + RPMsg 协议。

---

## 38.6 验证软核：在 QEMU 上跑同样的二进制

你的软核跑 RV32IM，QEMU 也能模拟 RV32IM。**在 QEMU 上先调通软件**，再下到 FPGA：

```bash
qemu-system-riscv32 -M virt -nographic -kernel my_app.elf
```

这避免在 FPGA 上调软件 bug（FPGA debug 比 QEMU 慢 10×）。

---

## 38.7 自检题

1. PicoRV32 跑 100 MHz 算快还是慢？为什么硬核能跑 GHz 而软核不行？
2. SoC 里两个 master 同时访问同一个 slave，怎么仲裁？
3. 异构多核为什么不全用 Cortex-A？
4. 软核能跑 Linux 吗？需要什么？

答案见 `code/answers.md`。

---

## 38.8 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| FPGA 全流程        | [39 FPGA 验证](../39_FPGA验证/)             |
| TrustZone 安全岛   | [40 嵌入式安全](../40_嵌入式安全/)         |
| RISC-V 在低功耗设计 | [41 低功耗设计](../41_低功耗设计/)         |
| RPMsg 异构通信     | [42 OTA](../42_OTA_固件升级/)              |

下一章 [39 FPGA 验证流程](../39_FPGA验证/) 看从 RTL 到 bitstream 的完整工程链。
