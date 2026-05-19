# 第 22 章　MIPI CSI / DSI：摄像头与屏幕的"专线"

> 现代设备里**屏幕、摄像头、5G 基带**几乎都走 MIPI 联盟定义的高速差分接口。这是 SoC 设计者每天打交道的协议，但软件层接触相对少 —— 因为大部分细节被驱动盖住了。本章给你足够的知识看懂硬件框图、读懂 datasheet 上 MIPI 那几页。
>
> **学完本章你应该能**：(1) 解释 D-PHY 的 lane 概念，(2) 区分 CSI-2（摄像头）和 DSI（屏幕）的应用面，(3) 看到 4-lane / 2-lane 知道意味着什么，(4) 知道 CSI / DSI 帧的"高层结构"。

---

## 22.1 MIPI 联盟和它的协议族

MIPI = **Mobile Industry Processor Interface**，2003 年成立的产业联盟。
为手机内部互联定义了一系列协议：

| 协议              | 用途                          |
|-------------------|-------------------------------|
| **D-PHY**         | 物理层，几乎所有 MIPI 都基于它 |
| **CSI-2**         | Camera Serial Interface       |
| **DSI**           | Display Serial Interface      |
| **DSI-2**         | 升级版                         |
| **C-PHY**         | 新一代物理层（3 线编码）       |
| **I3C**           | I²C 升级                       |
| **SoundWire**     | 音频                           |
| **DigRF**         | 数字基带 ↔ 射频              |

**绝大多数嵌入式工程师只会接触 CSI-2 + DSI**，本章聚焦这俩。

---

## 22.2 D-PHY：物理层基础

```
   Clock Lane    ─── 差分对 (CLK_P, CLK_N)
   Data Lane 0   ─── 差分对 (D0_P, D0_N)
   Data Lane 1   ─── 差分对 (D1_P, D1_N)
   ...
```

- **1 个 Clock Lane + 1~4 个 Data Lane**
- 每个 Lane 是差分对
- 速率：**1.5 Gbps 每 Lane** 标准；D-PHY 2.0 升到 4.5 Gbps；D-PHY 2.5 到 6 Gbps

每 Lane 两种模式：
- **HS (High-Speed)**：差分小摆幅 (~200 mV)、高速、低压差分
- **LP (Low-Power)**：单端 1.2 V CMOS、低速、用于控制和初始化

```
LP-11 ──→ LP-01 ──→ LP-00 (start of HS)──→ HS xx xx xx xx ...──→ HS-11 trail──→ LP-11
        ↑                                 ↑
        进入高速前的"低速握手"           真正的数据传输
```

**这个握手机制让 lane 在不传数据时进入超低功耗模式**，对手机续航关键。

---

## 22.3 CSI-2：摄像头到 SoC

```
        Camera Sensor                       SoC ISP
   ┌─────────────────┐                ┌──────────────┐
   │                 │ CSI-2 Lanes   │              │
   │  Bayer ROI ─→ ─┼────────────────┼─→ ISP ─→ DDR │
   │      MIPI PHY   │                │  Pipeline    │
   └─────────────────┘                └──────────────┘
              ↑
        I²C 控制 + GPIO (复位、电源)
```

**数据流方向**：相机 → SoC。  
**层级**：
- D-PHY 物理层
- PPI (PHY Protocol Interface)：连接 D-PHY 和协议层
- 协议层 (CSI-2)：定义帧格式

### CSI-2 帧结构

一帧图像 = 多行：

```
FS (Frame Start) packet
  Line 1: LS, pixel data, LE
  Line 2: LS, pixel data, LE
  ...
  Line N: LS, pixel data, LE
FE (Frame End) packet
```

- 每包带 **Virtual Channel ID** (VC, 2 bit) + **Data Type** (DT, 6 bit)
- 像素格式 (DT)：RAW8/10/12、YUV420/422、RGB888 等

VC 让一个 CSI-2 链路上时分复用多个数据流（多摄像头共享 link）。

### 实战：lane 数量怎么算

1080p 30 fps RAW10：
```
带宽 = 1920 × 1080 × 10 bit × 30 / 8 = ~78 Mbps × 10 = 780 Mbps
```

考虑包头开销和约 ~80% 效率 → 实际需要约 1 Gbps。**1 个 1.5 Gbps lane 够**。

4K 60 fps RAW12：
```
3840 × 2160 × 12 × 60 / 8 = ~7.5 Gbps
```

→ 需要 4 个 lane × 2.5 Gbps，或 D-PHY 2.0 + 2 lane。这就是为什么高端摄像头模块标着"4-lane MIPI"。

---

## 22.4 DSI：SoC 到屏幕

```
        SoC                              Display Panel
   ┌──────────────┐  DSI Lanes      ┌──────────────────┐
   │  GPU/Display ─┼─────────────────→ Timing Ctrl + LCD│
   │  Controller  │                  │     Driver IC    │
   └──────────────┘                  └──────────────────┘
```

**与 CSI-2 镜像方向**：SoC 主动推数据给屏幕。

DSI 工作两种模式：
- **Command Mode**：SoC 写到 panel 的 frame buffer，panel 自己定时刷新（panel 必须有 RAM）→ 省功耗，适合静态屏
- **Video Mode**：SoC 实时按行送像素，panel 没有 frame buffer → 适合视频流，但 SoC 端不能停

Video Mode 进一步分：
- Non-Burst：完全按 H/V sync 时序送
- Burst：高速送完一帧后进 LP，省功耗

---

## 22.5 C-PHY 简介

D-PHY 是 2 线差分。C-PHY 是 **3 线编码**，每条 lane 3 根线，用 3 个电平的 wire-state 编码 2.28 bits / symbol。

```
D-PHY: 1 lane = 2 wires, 1 bit / wire / cycle
C-PHY: 1 lane = 3 wires, 2.28 bit / 3 wires / symbol
```

**优势**：相同线数下吞吐高约 1.5×。**劣势**：编解码更复杂，PCB 走线讲究。  
高端手机摄像头开始用，但市场上 D-PHY 仍主流。

---

## 22.6 SoC 端 IP 结构

CSI-2 接收 IP 框架（典型）：

```
┌─────────────────────────────────────────────────────────────┐
│  D-PHY PHY     ←→  PHY Adapter   ←→   CSI-2 Decoder         │
│  (模拟+数字)        (PPI)              │                    │
│                                       ↓                    │
│                              ┌─────────────────┐            │
│                              │  Packet Parser │            │
│                              │  (FS/FE/LS/LE) │            │
│                              └─────────────────┘            │
│                                       ↓                    │
│                              ┌─────────────────┐    DMA    │
│                              │  Line Buffer   │ ─────────→ DDR
│                              └─────────────────┘            │
│                                       ↓                    │
│                              ┌─────────────────┐            │
│                              │  ISP / ML       │ -→ 进一步处理│
│                              └─────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

软件几乎不直接碰 PHY，**只配置 lane 数 / 像素格式 / VC**，然后告诉 DMA 一块 DDR buffer 等就行。Linux 的 V4L2 子系统提供这套抽象。

---

## 22.7 软件接触面

| 平台         | 抽象层                         |
|--------------|---------------------------------|
| Linux        | V4L2 (videodev2)，子设备模型     |
| Android      | Camera HAL                      |
| 裸机 / RTOS  | 厂商 SDK，直接配寄存器           |
| Yocto        | gst-libav / v4l-utils 集成        |

第 32 章 Linux 子系统驱动会回头讲 V4L2。

---

## 22.8 自检题

1. 一颗 1080p 60fps RGB888 屏幕走 DSI 至少需要多少带宽？4 lane 1.5 Gbps 够吗？
2. CSI-2 上的 VC（Virtual Channel）有什么实际用途？
3. D-PHY 进 HS 之前为什么先要走一段 LP 序列？
4. Command Mode DSI 屏幕的优势在什么场景下最明显？

答案见 `code/answers.md`。

---

## 22.9 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| 差分高速 + 源同步  | [06 总线与时序图](../06_总线与时序图/) 回顾  |
| Linux V4L2 / DRM   | [32 子系统驱动](../32_子系统驱动模型/)      |
| 边缘视觉 / AI 加速 | [43 边缘 AI](../43_边缘AI/)                  |
| 多 PHY 集成        | [38 集成软核 SoC](../38_集成软核SoC/)        |

下一章 [23 无线协议入门](../23_无线协议入门/) 离开有线，看 BLE / WiFi / LoRa 在嵌入式里的样子。
