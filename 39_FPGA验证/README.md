# 第 39 章　FPGA 验证流程

> 写好的 Verilog 怎么变成 FPGA（Field-Programmable Gate Array，现场可编程门阵列）上能跑的位流？这一章不深入特定厂家工具，而是讲**普适的工程流程**：仿真 → 综合（synthesis，将 HDL 代码转换为门级网表的过程）→ 布局布线（Place and Route，将门级网表映射到 FPGA 物理资源的过程）→ 时序收敛（Timing Closure，保证所有信号在时钟约束内建立/保持时间满足）→ 比特流（bitstream，将 RTL 逻辑映射到 FPGA 配置数据的二进制文件）。
>
> **学完本章你应该能**：(1) 画出 FPGA 设计完整流程图，(2) 区分功能仿真和时序仿真，(3) 解释什么是时序收敛 (Timing Closure)，(4) 知道 SDC 约束的作用。

---

![FPGA验证配图](images/fpga_flow.png)

## 39.1 七步流程

```
┌──────────────────────────────────────────────────────────────┐
│  1. RTL 编写       (Verilog/SystemVerilog/VHDL)               │
│  ↓                                                            │
│  2. 功能仿真       (Verilator / VCS / Questa)                │
│     "电路行为对吗？"                                          │
│  ↓                                                            │
│  3. 综合 (Synthesis)                                          │
│     RTL → 网表 (gate-level netlist)                           │
│     "把代码翻译成 LUT + FF"                                   │
│  ↓                                                            │
│  4. 布局布线 (Place & Route)                                  │
│     网表 → FPGA 的具体单元 + 走线                              │
│     "放到 FPGA 的哪个 LUT、哪条线"                            │
│  ↓                                                            │
│  5. 时序分析 (Static Timing Analysis, STA)                    │
│     "Fmax 多少？满足约束吗？"                                  │
│  ↓                                                            │
│  6. 时序仿真 (Timing simulation, 可选)                        │
│     带真实延迟跑仿真                                          │
│  ↓                                                            │
│  7. Bitstream 生成 + 下载                                     │
│     最终能下到 FPGA                                            │
└──────────────────────────────────────────────────────────────┘
```

![39.1 七步流程](images/generated/fpga_validation_flow_direct.png)

**整体流程类比软件开发**：写代码（RTL）→ 单元测试（功能仿真）→ 编译（综合）→ 链接+优化（布局布线）→ 性能测试（时序分析）→ 部署（下载 bitstream）。最大的不同是：软件编译可以在秒级完成，而 FPGA 的综合+布局布线对于大型设计可能需要数小时。

RTL（Register Transfer Level，寄存器传输级描述）是 Verilog/VHDL 设计的主要抽象层次，描述数据在 FF（Flip-Flop，触发器）之间如何流动和变换。

---

## 39.2 功能仿真：第一道工序

功能仿真在综合之前，使用 testbench（测试台：用于仿真验证的测试代码框架，不综合成硬件）来验证 RTL 逻辑的行为是否符合预期。这是发现逻辑 bug 成本最低的阶段——在这里改一行代码是秒级的，到了 FPGA 上调试则可能要花几小时。

Verilator（一个将 Verilog/SystemVerilog 编译为 C++ 仿真模型的开源工具）是开源高速仿真器：

```bash
verilator --binary -j 0 -O3 \
    --top-module tb_top \
    counter4.v tb_counter4.v

./obj_dir/Vtb_top
```

比 Icarus Verilog（iverilog，开源 Verilog 仿真器）快 10-100×。生产级数字 IC 验证（UVM（Universal Verification Methodology，通用验证方法学）、约束随机）大多走 Verilator + Cocotb（Python testbench）。

DUT（Device Under Test，被测设备/模块）在 testbench 中被实例化，testbench 产生激励信号并检查 DUT 的输出，VCD（Value Change Dump，值变化转储格式，波形文件格式）文件记录所有信号变化，可用 GTKWave（开源波形查看工具）可视化分析。

---

## 39.3 综合：把 RTL 变 LUT 网表

综合（synthesis）是将 HDL（Hardware Description Language，硬件描述语言）代码转换为门级网表的过程——即把你的抽象描述"翻译"成由 LUT（Look-Up Table，查找表，FPGA 的基本逻辑单元）、FF 和 BRAM（Block RAM，块存储器，FPGA 内置的存储资源）等 FPGA 基本单元组成的网络：

```bash
# yosys 开源综合工具
yosys -p "read_verilog counter4.v; synth_ice40 -top counter4 -json out.json"
```

输出 `out.json` 描述：用了几个 LUT、几个 FF、各自怎么连。

工具会**优化**：
- 死代码删除（gc-sections-like）
- 常量传播
- 资源共享（多个 always 块共用 ALU）
- 状态机重编码（binary → one-hot）
- 寄存器重定时 (Retiming)：把 FF 移动到关键路径外提升 Fmax

CLB（Configurable Logic Block，可配置逻辑块）是 FPGA 中包含 LUT 和 FF 的基本逻辑单元组合；IOB（Input/Output Block，输入输出块）是 FPGA 连接外部引脚的接口单元；综合后的资源使用报告会列出这些单元的占用情况，帮助你评估设计是否适合目标器件。

---

## 39.4 布局布线：决定时序的关键

布局布线（Place and Route）将门级网表映射到 FPGA 物理资源的过程：

```bash
# nextpnr 开源布局布线
nextpnr-ice40 --hx8k --json out.json \
    --pcf pinmap.pcf --asc out.asc
```

工具做的事：
- **Placement（布局）**：每个 LUT / FF 放到 FPGA 阵列的哪一格（CLB）
- **Routing（布线）**：把各信号用通用路由资源连起来
- **Timing-driven（时序驱动）**：尽量让关键路径走短的连线

输出 `.asc` （ICE40）或 `.bit` （Xilinx）位流。

布局布线的质量直接决定时序：两个 FF 之间的物理距离越远，信号传播延迟越大，能达到的最高工作频率（Fmax）就越低。这也是为什么布局布线是整个流程中最耗时、最影响结果的步骤。PLL（Phase-Locked Loop，锁相环，用于时钟生成和分频）和 DLL（Delay-Locked Loop，延迟锁定环）是 FPGA 内置的时钟管理单元，布局时需要合理规划时钟信号的走线。

---

## 39.5 时序约束 SDC

布线工具不知道你要的目标频率，需要你**写 SDC（Synopsys Design Constraints，Synopsys 设计约束文件格式，被各大 EDA 工具广泛支持）**：

```sdc
create_clock -name clk -period 10.0 [get_ports clk]         # 100 MHz
set_input_delay  -clock clk -max 2.0 [get_ports rx]
set_output_delay -clock clk -max 2.0 [get_ports tx]
set_false_path -from [get_ports rst_n] -to [all_registers]   # 异步复位
set_false_path -through [get_pins sync_ff[0].in]             # CDC 同步器
```

SDC 约束的作用：
- `create_clock`：告诉工具时钟频率目标，工具据此计算每条路径的 slack
- `set_input_delay` / `set_output_delay`：约束 IO 引脚的时序余量
- `set_false_path`：告诉工具某些路径不需要时序检查（如 CDC（Clock Domain Crossing，跨时钟域问题）同步器的输入、异步复位路径）

工具基于 SDC 做 **STA（Static Timing Analysis，静态时序分析）**：枚举每条触发器到触发器路径，算总延迟，对比时钟周期 → **slack**：

```
slack = T_clk_period - (T_clk2q + T_combinational + T_setup)

slack ≥ 0 : 满足
slack < 0 : 违反 → 调代码或降频
```

---

## 39.6 时序收敛 (Timing Closure)

时序收敛（Timing Closure）：保证所有信号在时钟约束内建立/保持时间满足，即"所有路径的 slack ≥ 0"的迭代过程。失败时手段：

1. **流水线化** 关键路径（最有效）
2. **手动重定时**：把 always 切成几段
3. **降低目标频率**（最后选择）
4. **resource sharing** 减少切换
5. **改物理约束**：固定关键 IP 核的位置

商用 FPGA 项目常常**最后 10% slack 调一个月**。"95% 拥塞 + 时序爆炸" 是行业梗。

**流水线化（Pipelining）是最有效的手段**：在一条长组合逻辑路径的中间插入寄存器（FF），把一个"很长的延迟"拆成"两个较短的延迟"，代价是增加了一个时钟周期的延迟（latency），但吞吐量（throughput）不变甚至提高。

---

## 39.7 时序仿真：带延迟的仿真

布线后工具生成 `*.sdf` 文件，描述每个门的实际延迟。**时序仿真**用这些延迟跑测试：

```
功能仿真：所有信号变化"立即"传播
时序仿真：每个门有真实延迟，仿真显示毛刺、setup/hold 违例
```

时序仿真慢、但能发现纯静态 STA 抓不到的功能 bug（如 CDC 路径未约束）。

---

## 39.8 下载与调试

下载方式：
- **JTAG**：所有 FPGA 都支持，速度慢但通用
- **USB-Blaster / FT2232**：调试器
- **快速配置**：直接从外置 SPI Flash 加载（生产配置）

板上调试：
- **Vivado ILA（Integrated Logic Analyzer，集成逻辑分析仪）**：在 FPGA 内部嵌入采样器，把指定信号波形拉到电脑看。等于"嵌入式逻辑分析仪"
- **Xilinx VIO / Intel Signal Tap**：类似

**这套是 FPGA 工程师真正调 bug 的姿势** —— 实芯片上看波形。

ILA 的工作原理：在 FPGA 内部额外综合一小块"采样器"逻辑，将你关注的信号连接过去，触发条件满足时把信号值存入 BRAM（Block RAM，块存储器，FPGA 内置的存储资源），然后通过 JTAG 传输到 PC，在 Vivado 界面以 VCD（Value Change Dump，值变化转储格式）样式显示。这比传统串口 printf 调试强得多，因为它能抓到纳秒级的时序问题。

---

## 39.9 开源 vs 商用工具

| 工具           | 类型     | FPGA              |
|----------------|----------|-------------------|
| yosys + nextpnr | 开源    | ICE40, ECP5, Xilinx 7 系列试验性 |
| Xilinx Vivado  | 免费 / 商用 | Xilinx / AMD     |
| Intel Quartus  | 免费 / 商用 | Intel / Altera   |
| Lattice Diamond | 免费    | Lattice           |
| Microsemi Libero | 商用   | PolarFire 等       |

学习 / 玩具项目：**开源全套** + ICE40 / ECP5 板。
工业项目 / 高端 FPGA：**Vivado / Quartus**。

---

## 39.10 一份完整迷你流水线

`code/` 里有一个最小工程：counter4 + 顶层 + pinmap，跑 yosys + nextpnr 出 ICE40 bitstream。

```bash
make            # 综合 + PnR + 生成 .bin
make program    # 下载（需 iceprog + 物理板）
```

或仅做综合检查：
```bash
yosys -p "read_verilog counter4.v top.v; synth_ice40 -top top -json out.json"
```

---

## 39.11 自检题

1. 综合后的代码和你写的 RTL 不一样了，为什么？
2. 时序违反 (negative slack) 的根本原因总是"时钟太快"吗？
3. SDC 里 `set_false_path` 用在哪些场景？
4. ILA / Signal Tap 比传统串口 printf 调试好在哪？

答案见 `code/answers.md`。

---

## 39.12 与后续章节的联系

| 概念                  | 下游章节                                  |
|-----------------------|-------------------------------------------|
| 安全 IP 的硬件验证     | [40 嵌入式安全](../40_嵌入式安全/)         |
| FPGA + AI 加速器       | [43 边缘 AI](../43_边缘AI/)                |
| FPGA 在功能安全产品中 | [44 功能安全](../44_功能安全与编码规范/)    |
| Rust HDL              | [45 Embedded Rust](../45_Embedded_Rust/)   |

---

## Part 6 收尾

Part 6 SoC / FPGA 5 章完成：

| 章 | 主题            | 关键收获                          |
|----|-----------------|-----------------------------------|
| 35 | Verilog 入门    | 硬件 vs 软件思维、`<=` vs `=`       |
| 36 | FSM 可综合      | 三段式、可综合规则、UART RX 实例    |
| 37 | 片上总线        | AXI/AHB/APB 三层、valid/ready       |
| 38 | 集成 SoC        | 软核 vs 硬核、异构多核              |
| 39 | FPGA 验证        | 七步流程、SDC、时序收敛             |

下一部分 [Part 7 进阶专题](../40_嵌入式安全/)：安全、低功耗、OTA、AI、功能安全、Rust。
