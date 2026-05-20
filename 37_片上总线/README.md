# 第 37 章　片上总线：AXI / AHB / APB

> SoC 内部几十个 IP 核（CPU、DMA、UART、Ethernet、GPU...）通过 **片上总线** 互联。ARM 公司的 AMBA 标准（AXI / AHB / APB）是事实业界标准。这一章给你这三种总线的世界观。
>
> **学完本章你应该能**：(1) 区分 AXI / AHB / APB 各自的定位，(2) 看懂 AXI 的 5 个通道，(3) 解释 valid/ready 握手，(4) 知道为什么 SoC 上有桥 (bridge)。

---

![片上总线配图](images/soc_bus_hierarchy.png)

## 37.1 三个总线，三个层级

ARM AMBA 协议族，按性能从高到低：

| 总线 | 全称                       | 性能等级         | 用在哪              |
|------|----------------------------|------------------|---------------------|
| AXI  | Advanced eXtensible Interface | 高性能、流水化 | CPU ↔ 内存、CPU ↔ DMA、CPU ↔ 高带宽外设 |
| AHB  | Advanced High-performance Bus | 中性能         | 中端外设、老 SoC      |
| APB  | Advanced Peripheral Bus    | 低性能、简单    | 低速外设（UART/GPIO/RTC） |

一个典型 SoC：

```
        ┌──────────┐           ┌──────────┐
        │   CPU    │ ←─ AXI ─→ │   DDR    │
        └──────────┘           │ Controller│
              ↑                └──────────┘
            AXI
              ↓
        ┌──────────┐ ←AXI→  GPU/ISP/AI
        │   AXI    │
        │ 互连     │ ←AXI→  DMA
        └─┬────────┘
          │ AXI-to-AHB 桥
        ┌─┴────────┐ ←AHB→ Ethernet / USB / 中速外设
        │   AHB    │
        │ 互连     │
        └─┬────────┘
          │ AHB-to-APB 桥
        ┌─┴────────┐ ←APB→ UART/SPI/I2C/GPIO/RTC
        │   APB    │
        │ 互连     │
        └──────────┘
```

![37.1 三个总线，三个层级](images/ascii/ascii_01_37_1_69b54ab7.png)

层级化是为了**性能与复杂度平衡**：CPU 跑得快，但 UART 一个寄存器 32 字节足够，没必要走 AXI 的全部握手开销。

---

## 37.2 APB：最简单

每次访问要 2-3 个时钟周期，**单向**，**无并发**：

```
   PCLK    ──╱──╲__╱──╲__╱──╲__
   PSEL    ──┬─────────────────
              │
   PENABLE ──┬───┬─────────────
                  │
   PADDR  ═══<──A──>═══════════
   PWRITE ═══<──W──>═══════════
   PWDATA ═══<──D──>═══════════
   PREADY ─────────┬────┬──────
                     ↑
                  完成
```

![37.2 APB：最简单](images/ascii/ascii_02_37_2_apb_46a024ce.png)

握手周期：
1. **SETUP 阶段**：PSEL=1，PENABLE=0，给地址数据
2. **ACCESS 阶段**：PENABLE=1，等 PREADY 拉高表示完成

最少 2 周期，慢但简洁。**APB IP 只需 ~20 行 Verilog**。

---

## 37.3 AHB：管道化的升级

支持 **pipelined access**：地址相位和数据相位重叠，吞吐翻倍：

```
   HCLK   ──╱─╲__╱─╲__╱─╲__╱─╲__
   HADDR  ═══<A1><A2><A3>══
   HWDATA ═══════<D1><D2>══
   HRDATA ═══════<D1><D2>══
   HREADY ────┬─────┬─────┬───
              ↑     ↑     ↑
            事务完成
```

![37.3 AHB：管道化的升级](images/ascii/ascii_03_37_3_ahb_ea8a8ab5.png)

AHB-Lite 是简化版（去掉 burst 仲裁），常用于单主多从场景。

支持 burst（连续多字访问）但**单主独占总线**，多主要做仲裁。

---

## 37.4 AXI：五通道独立

AXI4 是真正的"现代"总线：

```
            ┌────────── AW (Write Address) ──────────→
            ├────────── W  (Write Data) ─────────────→
   Master                                                Slave
            ←────────── B  (Write Response) ──────────
            ├────────── AR (Read Address) ─────────────→
            ←────────── R  (Read Data) ────────────────
```

![37.4 AXI：五通道独立](images/ascii/ascii_04_37_4_axi_f5872a78.png)

**5 个独立通道**，每个通道独立 valid/ready 握手：

```
   valid     ─────┌────────────  (master 有数据)
   ready     ─────────┌────────  (slave 准备好收)
                       ↑
                  此拍传输发生
```

![37.4 AXI：五通道独立](images/ascii/ascii_05_37_4_axi_0c97fe86.png)

带来的能力：
- **完全乱序**：write 和 read 不阻塞彼此
- **outstanding**：多个 read 请求飞在路上，按 ID 排序响应
- **burst**：一次握手覆盖最多 256 个 beat
- **不同 burst 长度并行**：A 还在传，B 已经开始

代价：协议复杂，单 IP 的状态机比 APB 大 10×。

### AXI4 vs AXI4-Lite vs AXI4-Stream

| 版本          | 用途                              |
|---------------|-----------------------------------|
| AXI4-Lite     | 简化版，单 beat，常用于配置寄存器（APB 替代）|
| AXI4          | 完整 burst + outstanding，CPU↔内存 |
| AXI4-Stream   | 单向流，无地址，只有数据，DSP / 视频流 |

---

## 37.5 valid/ready 协议规则（第 06 章再加深）

```
握手规则：
  - 当 valid=1 时，master 不能撤 valid 直到 ready=1
  - ready 可以提前拉高（贪婪型）
  - 一拍 valid=1 && ready=1，数据被采走
  - 不能用 valid 作为 ready 的组合输入（避免组合回路）
```

最后一条是 AXI 协议最大坑：**ready 不能依赖 valid**，否则会产生死锁或时序问题。

---

## 37.6 一个 AXI4-Lite 从机骨架（Verilog）

```verilog
module axil_slave (
    input  wire        ACLK, ARESETn,
    input  wire [31:0] AWADDR, input wire AWVALID, output reg  AWREADY,
    input  wire [31:0] WDATA,  input wire WVALID,  output reg  WREADY,
    output reg  [1:0]  BRESP,  output reg  BVALID, input  wire BREADY,
    input  wire [31:0] ARADDR, input wire ARVALID, output reg  ARREADY,
    output reg  [31:0] RDATA,  output reg [1:0] RRESP, output reg RVALID, input wire RREADY
);
    /* 内部寄存器 */
    reg [31:0] reg_a, reg_b;

    /* 写通道：等 AW + W 都来才完成 */
    always @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            AWREADY <= 0; WREADY <= 0; BVALID <= 0;
        end else begin
            AWREADY <= AWVALID & !AWREADY;       // 单拍 ready
            WREADY  <= WVALID  & !WREADY;
            if (AWVALID && AWREADY && WVALID && WREADY) begin
                case (AWADDR[7:0])
                    8'h00: reg_a <= WDATA;
                    8'h04: reg_b <= WDATA;
                    default: ;
                endcase
                BRESP  <= 2'b00;     // OK
                BVALID <= 1;
            end else if (BVALID && BREADY) begin
                BVALID <= 0;
            end
        end
    end

    /* 读通道 */
    always @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            ARREADY <= 0; RVALID <= 0;
        end else begin
            ARREADY <= ARVALID & !ARREADY;
            if (ARVALID && ARREADY) begin
                case (ARADDR[7:0])
                    8'h00: RDATA <= reg_a;
                    8'h04: RDATA <= reg_b;
                    default: RDATA <= 32'hDEAD_BEEF;
                endcase
                RRESP  <= 2'b00;
                RVALID <= 1;
            end else if (RVALID && RREADY) begin
                RVALID <= 0;
            end
        end
    end
endmodule
```

写一份这样的从机 + 跑 testbench 是 SoC 集成的"hello world"，每个 FPGA 工程师都做过。

---

## 37.7 互连 / 交叉开关

多个 master + 多个 slave 互联，工具会综合一个 **crossbar**：

```
       ┌─── CPU ───┐
       │           │
       ├─── DMA ───┤
       │  Crossbar │
       ├─── GPU ───┤
       │           │
       └────────┬──┘
                ├──── DRAM Ctrl
                ├──── SRAM
                ├──── 外设域
                └────  ...
```

![37.7 互连 / 交叉开关](images/ascii/ascii_06_37_7_a5cbaecb.png)

Xilinx Vivado、Intel Quartus 都有 IP 生成器，画框框 + 连线生成 SystemVerilog 互连。手写互连罕见（除非超紧资源）。

---

## 37.8 自检题

1. 同一颗 SoC 里为什么不能全部用 AXI，要分层 AHB / APB？
2. AXI write 和 read 通道独立，能不能在同一拍同时发起 read 和 write 请求？
3. valid/ready 握手为什么 ready 不能"看到" valid 才拉高？
4. APB 改成时钟拉伸（PREADY 长时间不拉高），会发生什么？

答案见 `code/answers.md`。

---

## 37.9 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| 软核 CPU 接 AXI    | [38 集成软核 SoC](../38_集成软核SoC/)      |
| FPGA Vivado IP    | [39 FPGA 验证](../39_FPGA验证/)             |
| AXI Coherent Port | [27 实时性深入](../27_实时性深入/) Cache    |
| MMIO + AXI-Lite    | [10 GPIO 寄存器](../10_第一个程序_GPIO/) 回顾 |

下一章 [38 集成软核 SoC](../38_集成软核SoC/) 把 CPU + 总线 + 外设组装成一颗"自己设计的芯片"。
