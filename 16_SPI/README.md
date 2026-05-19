# 第 16 章　SPI：同步串行的"裸"协议

> UART 是异步的，SPI 是**同步**的 —— 多了一根时钟线，所有事情都踩在时钟边沿上。SPI 简单、快、可达几十 / 几百 Mbps，是 Flash / 显示器 / SD 卡 / 传感器的事实标准。
>
> **学完本章你应该能**：(1) 解释 CPOL/CPHA 四种模式，(2) 看一眼时序图判断模式对不对，(3) 知道菊花链 / 多从机选片的两种连接姿势，(4) 理解 QSPI / OSPI 在主流 SPI 上加了什么。

---

## 16.1 四根线

```
主 (Master)                       从 (Slave)
                                   
SCK   ─────────────────────────→ SCK    (主驱动)
MOSI  ─────────────────────────→ MOSI   (Master Out, Slave In)
MISO  ←───────────────────────── MISO   (Master In,  Slave Out)
nCS   ─────────────────────────→ nCS    (片选，低有效)
```

加 GND 共 **5 根**。一根多从就再加一根 nCS。

**核心特性**：
- 全双工：MOSI 和 MISO 同时传，一拍发一拍收
- 同步：所有信号踩 SCK 边沿
- 主单一：只有一个主（multi-master 极少，常规说"SPI 主从架构"）
- 一根 nCS = 一个从

---

## 16.2 CPOL / CPHA：让人迷糊的"四模式"

时钟有两件事可调：
- **CPOL (Clock POLarity)**：空闲电平。0 = 空闲低；1 = 空闲高。
- **CPHA (Clock PHASE)**：在哪个沿采样。0 = 第一个沿采、第二个沿改；1 = 第二个沿采、第一个沿改。

四种组合：

| Mode | CPOL | CPHA | 空闲 | 采样沿        | 谁常用         |
|------|------|------|------|---------------|----------------|
| 0    | 0    | 0    | 低   | SCK 上升沿    | 最常见，SD/Flash |
| 1    | 0    | 1    | 低   | SCK 下降沿    | 少             |
| 2    | 1    | 0    | 高   | SCK 下降沿    | 少             |
| 3    | 1    | 1    | 高   | SCK 上升沿    | 部分传感器     |

```
Mode 0 时序：
SCK   ___╱──╲__╱──╲__╱──╲___
MOSI  ═b7══b6══b5══b4═════
            ↑    ↑    ↑    采样在每个上升沿
```

**主从两边 CPOL/CPHA 必须一致**，错了表现就是全 0 或全 F。

---

## 16.3 多从机的两种姿势

### ① 多 nCS（最常用）

```
   主    ─── SCK ────┬─────────┬───────
         ─── MOSI ───┤         │
         ←── MISO ───┤         │
         ─── nCS_A ──┘   ─── nCS_B ──┘
              ↓             ↓
            Slave A       Slave B
```

每个从机一根 nCS。主一次只激活一个从。简单可靠。

### ② 菊花链 (Daisy Chain)

```
   主 ─── SCK ─→ A ─SCK→ B ─SCK→ C
       MOSI ─→ A ─MISO→ B ─MISO→ C ─MISO→ 主
       nCS ─────────┴───────┴─────
```

所有从机共享 nCS，**MISO 串成长移位寄存器**。主送 N×8 比特，每个从拿到一个字节。省线但要从机硬件支持。

工业 ADC 多通道时用得多。

---

## 16.4 SPI IP 核内部

```
┌────────────────────────────────────────────────────────────┐
│   ┌──────┐    ┌──────────┐    ┌──────────┐                  │
│   │ 总线 │    │ TX FIFO  │    │ 移位寄存器│                  │
│   │ 接口 │───→│  (8 深)   │───→│  TX (并→串)─→ MOSI         │
│   │      │    └──────────┘    │           │                 │
│   │ APB  │    ┌──────────┐    │  RX (串→并)←─ MISO         │
│   │      │←───│ RX FIFO  │←───│           │                 │
│   │      │    └──────────┘    └──────────┘                  │
│   │      │                          ↑                       │
│   └──────┘                          │                       │
│                                  ┌──────────┐               │
│                  CPOL/CPHA ────→ │ SCK 生成 │── SCK         │
│                                  │ + 计数器 │               │
│                                  └──────────┘               │
└────────────────────────────────────────────────────────────┘
```

**和 UART 的区别**：
- 没有"起始位下降沿检测"，因为时钟由主驱动
- 没有过采样，发送方 = 时钟方
- 全双工：TX shift 和 RX shift 同时在动

**SCK 生成 = 分频器** + CPOL/CPHA 配置。多数 IP 还提供 prescaler 让 SCK = clk / (2N)。

---

## 16.5 时序图再读一次

回顾第 06 章的 SPI 主时序图：

```
SCK   ──╱──╲__╱──╲__╱──╲__
nCS   ─┐                  ┌──
       └──────────────────┘
MOSI  ═<b7><b6><b5><b4>══
MISO  ═<b7><b6><b5><b4>══
         ↑   ↑   ↑   ↑    Mode 0 在每个上升沿采样
```

datasheet 关键参数（PL022 风格）：
- `t_su(DI)`：MOSI 在采样沿前要稳定多久
- `t_h(DI)`：采样沿后还要保持多久
- `t_v(DO)`：SCK 边沿到 MISO 稳定的时间
- `f_SCK_max`：最大 SCK 频率

这些就是第 06 章 §6.6 所谓"协议层 setup/hold"。

---

## 16.6 QSPI / OSPI：变宽不变深

普通 SPI 一拍传 1 bit。**QSPI (Quad SPI)** 把 MOSI/MISO 扩成 4 根线，一拍传 4 bit。**OSPI (Octal SPI)** 扩到 8 根线。

```
SPI:    SCK  MOSI/MISO 各 1 根
QSPI:   SCK  IO[3:0] 双向 4 根
OSPI:   SCK  IO[7:0] 双向 8 根 + DQS strobe
```

**用途**：高速 NOR Flash（QSPI Flash 是 MCU 主流外置 Flash 形式）。MCU 集成 **QSPI 控制器** 后能让 CPU 通过 **XIP (eXecute-In-Place)** 直接从外置 QSPI Flash 取指令运行，无需先拷到 RAM。

OSPI 加 DQS（数据选通）= **源同步信号**（第 06 章 §6.2），让接收端用发送端时钟采样，能跑到几百 Mbps。

---

## 16.7 LM3S6965 SSI（=SPI 的官名）实战

LM3S 把 SPI 叫 **SSI (Synchronous Serial Interface)**，兼容 Motorola SPI / TI Synchronous Serial / National Microwire。

```c
#define SSI0_BASE       0x40008000u
#define SSI0_CR0        (*(volatile uint32_t *)(SSI0_BASE + 0x000u))
#define SSI0_CR1        (*(volatile uint32_t *)(SSI0_BASE + 0x004u))
#define SSI0_DR         (*(volatile uint32_t *)(SSI0_BASE + 0x008u))
#define SSI0_SR         (*(volatile uint32_t *)(SSI0_BASE + 0x00Cu))
#define SSI0_CPSR       (*(volatile uint32_t *)(SSI0_BASE + 0x010u))

#define SSI_SR_TNF      (1u << 1)   /* TX FIFO Not Full */
#define SSI_SR_RNE      (1u << 2)   /* RX FIFO Not Empty */

void ssi0_init(void)
{
    /* 时钟 / GPIO 略 */
    SSI0_CR1  = 0;                 /* 关，配寄存器 */
    SSI0_CPSR = 2;                 /* 偶数预分频 */
    SSI0_CR0  = (0u << 6)          /* SPO=0 (CPOL=0) */
              | (0u << 7)          /* SPH=0 (CPHA=0) */
              | (0u << 0)          /* FRF: Motorola SPI */
              | (7u << 0);         /* DSS = 8 bit */
    SSI0_CR1  = (1u << 1);         /* SSE: 使能 */
}

uint8_t ssi0_xfer(uint8_t b)
{
    while ((SSI0_SR & SSI_SR_TNF) == 0) {}
    SSI0_DR = b;
    while ((SSI0_SR & SSI_SR_RNE) == 0) {}
    return (uint8_t)(SSI0_DR & 0xFFu);
}
```

`code/spi_demo.c` 是完整版（QEMU 上 SSI 模拟有限，主要用于建立编程模板）。

---

## 16.8 Verilog: SPI 主机 FSM

第 06 章 `code/spi_master.v` 已经写过简化版。重点回顾 FSM：

```
   ┌─ IDLE ─→ (start=1) ─→ TRANSFER ─→ (count == 8) ─→ DONE ─→ IDLE
   │              ↑               │
   │              │  每 SCK 半周期 │
   │              └────────────────┘
   │
   └─ 输出 nCS=1, SCK 静默
   TRANSFER 中:
     - 半周期翻 SCK
     - 上升沿 (mode0) 移入 MISO 一位
     - 下降沿 (mode0) 移出 MOSI 下一位
```

---

## 16.9 自检题

1. SPI 模式 0 和 模式 3 都在 SCK 上升沿采样，差别在哪？
2. SD 卡可以用 SPI 或 SD 总线两种接法，SPI 接法的最大速率是多少？为什么慢？
3. 菊花链多从机为什么需要从机的硬件配合，不是软件能搞？
4. QSPI Flash 跑 XIP 时 CPU 取指延迟相比内部 Flash 大约高多少倍？

答案见 `code/answers.md`。

---

## 16.10 与后续章节的联系

| 概念                | 下游章节                                |
|---------------------|-----------------------------------------|
| SPI Flash + XIP     | [38 集成软核 SoC](../38_集成软核SoC/)     |
| 同步时序参数        | [05 数字电路与时序](../05_数字电路与时序/) 回顾 |
| QSPI 控制器 IP      | [37 AXI/AHB/APB](../37_片上总线/)         |
| SD 卡 / eMMC 协议    | [29 Buildroot](../29_交叉编译_Buildroot/) 镜像存储 |

下一章 [17 I²C / SMBus](../17_I2C_SMBus/) 把"主从一对一"换成"多主多从共享两根线"。
