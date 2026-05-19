# 第 19 章　USB 概览：插拔即用背后的复杂

> USB 是嵌入式领域里**最复杂**的协议之一 —— 一个完整 USB 主机栈代码量轻松超过 10 万行。这一章不教你写驱动，但让你理解：**插上一根 USB 线时背后发生了什么**，descriptor 和 enumeration 是什么，class driver 是什么意思。
>
> **学完本章你应该能**：(1) 解释 USB 的拓扑（Host-centric）和事务模型，(2) 描述设备插入时的枚举过程，(3) 知道四种 transfer 类型和它们的取舍，(4) 看到 CDC/HID/MSC/UVC 知道是什么 class。

---

## 19.1 USB 的世界观：Host-centric

USB 不是 peer-to-peer。**总是有一个 Host (主机)**，连接 N 个 **Device (设备)**。设备只有被询问时才发数据 —— 这是 USB 简化协议、降低设备硬件成本的核心选择。

```
   Host
    │
    └── HUB ──┬── Device A (键盘)
              ├── Device B (鼠标)
              ├── HUB ──┬── Device C (摄像头)
              │         └── Device D (U 盘)
              └── Device E (Wi-Fi 适配器)
```

- 1 个 Host 最多 127 个设备（地址 7 位）
- 树形拓扑，HUB 中转
- USB-C 引入了 USB-PD（电源协商）和"双角色"（设备可以变 Host）但模型基本未变

---

## 19.2 物理层与速率

| 标准              | 速率           | 线对                    |
|-------------------|----------------|-------------------------|
| USB 1.1 Low-Speed | 1.5 Mbps      | D+/D-（差分一对）        |
| USB 1.1 Full-Speed| 12 Mbps       | 同上                    |
| USB 2.0 High-Speed| 480 Mbps      | 同上 + 协议升级          |
| USB 3.0           | 5 Gbps        | 同上 + SuperSpeed 一对   |
| USB 3.1 Gen 2     | 10 Gbps       | 同上                    |
| USB 3.2 Gen 2x2   | 20 Gbps       | 双 SuperSpeed 对         |
| USB4 / Thunderbolt 3+ | 20 / 40 Gbps  | 多对 + PCIe 隧道         |

**USB 2.0 / FS / LS 共用 D+ / D-** 差分对。**USB 3.0+ 额外加 SuperSpeed 对** 物理上分离，向后兼容靠 mux。

物理层细节属于"PHY 工程"，本章不展开。

---

## 19.3 设备枚举：插上之后

```
1. 物理插入 → Host 检测到 D+/D- 上拉变化
2. Host 复位设备（拉低 D+/D- 一段时间）
3. Host 给设备发 GET_DESCRIPTOR(DEVICE) → 设备返回 18 字节描述符
4. Host 用一个新地址 SET_ADDRESS(addr) → 设备改用新地址
5. Host 拿配置描述符 / 接口描述符 / 端点描述符
6. Host 选一个配置 SET_CONFIGURATION(1) → 设备就绪
7. Host 加载对应 class driver → 设备可用
```

第 3–6 步全部通过 **端点 0 控制传输** 走。这是为什么所有 USB 设备都得实现 **EP0 = Default Control Pipe**。

---

## 19.4 Descriptor：设备的"自我介绍"

USB 设备的所有元数据都用描述符表达，分层嵌套：

```
Device Descriptor
 └─ Configuration Descriptor
     └─ Interface Descriptor   (一个设备可以有多个 Interface)
         └─ Endpoint Descriptor (每个 Interface 有 1+ Endpoint)
```

最重要几个字段：

**Device Descriptor**:
- `idVendor` / `idProduct`：VID / PID，全球唯一识别设备厂商和型号（VID 要花钱买）
- `bDeviceClass`：大类（HID/MSC/CDC/Vendor...）
- `bcdUSB`：支持的 USB 版本

**Interface Descriptor**:
- `bInterfaceClass`：实际的功能类
- `bInterfaceSubClass` / `bInterfaceProtocol`

**Endpoint Descriptor**:
- `bEndpointAddress`：端点号 + 方向 (IN/OUT)
- `bmAttributes`：传输类型（控制 / 中断 / 批量 / 等时）
- `wMaxPacketSize`：单包大小（FS 8/16/32/64，HS 最高 1024）

---

## 19.5 四种 Transfer 类型

| 类型           | 用途                       | 特点                              |
|----------------|----------------------------|-----------------------------------|
| **Control**    | 配置、命令                  | 必须成功，带握手，CRC 校验          |
| **Interrupt**  | 键盘、鼠标、HID            | 定期轮询，低延迟保证                |
| **Bulk**       | U 盘、打印机、串口转换器     | 大块数据，可被挤兑                 |
| **Isochronous**| 音频、视频                  | 固定带宽，**不保证数据完整性**     |

设备申报"我要 X kbps 带宽"，Host 按总带宽预算分配。**总带宽预算才是 Host 排程的核心约束**。

---

## 19.6 Class Drivers：标准化的"功能模板"

USB 强制把设备分类到 class，每个 class 有标准协议，**Host 端通用 driver** 处理：

| Class        | 缩写  | 例子                  |
|--------------|-------|-----------------------|
| HID          | 0x03  | 键盘、鼠标、游戏手柄   |
| Mass Storage | 0x08  | U 盘、SD 读卡器        |
| CDC          | 0x02  | 虚拟串口、网卡         |
| Audio        | 0x01  | USB 麦克 / 耳机        |
| Video (UVC)  | 0x0E  | 摄像头                 |
| Hub          | 0x09  | USB Hub                |
| Printer      | 0x07  | 打印机                 |
| Vendor       | 0xFF  | 自定义（要装专门驱动） |

这是为什么"插上键盘就能用"：HID Class 把按键报告格式标准化了，Windows / macOS / Linux 自带通用 HID driver。

---

## 19.7 嵌入式做 USB 的两种姿势

### ① USB Device（最常见）

MCU 当设备端，靠 USB Device IP + 外部 PHY 接 D+/D-：

```c
// Tinyusb / Cherry USB 等开源协议栈给你写 descriptor 回调和数据回调
// 几百行代码就能让 MCU 变成虚拟串口 / U 盘 / HID
```

### ② USB Host

Cortex-A 类 SoC 自带 EHCI/xHCI 主控制器。MCU 上偶尔有 OTG 控制器能切到 host 模式。Host 复杂度比 device 高一个数量级（要管理 hub 树、多设备调度、电源协商）。

### ③ USB OTG

设备能在 host 和 device 间切换。手机典型用法。

---

## 19.8 协议栈分层

```
┌─────────────────────────────────────┐
│  应用 (HID, MSC, CDC...)            │
├─────────────────────────────────────┤
│  Class Driver                       │
├─────────────────────────────────────┤
│  USB Core (枚举、Transfer 调度)      │
├─────────────────────────────────────┤
│  Host Controller Driver             │
│  (EHCI / xHCI / OTG)                │
├─────────────────────────────────────┤
│  Host Controller HW                 │
├─────────────────────────────────────┤
│  PHY                                │
├─────────────────────────────────────┤
│  D+ / D-（USB 2.0）+ SS 对（USB 3）  │
└─────────────────────────────────────┘
```

Linux 内核的 `drivers/usb/` 就是这套分层的工业实现。第 31 章会回到 Linux USB 驱动。

---

## 19.9 QEMU 上玩 USB

QEMU 可以模拟 USB Host + 把宿主机设备透传：

```bash
qemu-system-x86_64 \
  -usb -device usb-tablet \
  -device usb-host,vendorid=0x05ac,productid=0x024f
```

或加一个 USB 串口转换器虚拟设备。本章不深入，留给第 31 章 Linux 驱动一起。

---

## 19.10 自检题

1. 为什么 USB 是 host-centric？这种设计对设备端有什么好处？
2. 描述符里 idVendor / idProduct 必须全球唯一，怎么获得？
3. 音频流走 Isochronous transfer 而不是 Bulk 的核心原因是什么？
4. 你想让 MCU 看起来像 U 盘，要实现哪个 Class？

答案见 `code/answers.md`。

---

## 19.11 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| Class driver 模式 | [31 字符设备驱动](../31_字符设备驱动入门/) |
| USB CDC = 虚拟串口  | [15 UART](../15_UART/) 回顾                 |
| USB MSC = U 盘    | [29 Buildroot](../29_交叉编译_Buildroot/)   |
| PCIe 与 USB3 对比  | [21 PCIe 概念](../21_PCIe概念/)             |

下一章 [20 Ethernet + TCP/IP 速通](../20_Ethernet_TCPIP/) 进入计算机网络的世界。
