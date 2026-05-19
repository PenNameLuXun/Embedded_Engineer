# 第 26 章　Zephyr 上手：一个现代 RTOS 长什么样

> FreeRTOS 是经典 RTOS 的代表，Zephyr 则是"现代 RTOS"的代表 —— 它把 Linux 的设计哲学（**设备树 + Kconfig + 子系统化**）搬进了 RTOS 世界。这一章给你 Zephyr 的总体地图，让你看到 RTOS 也能"很大"。
>
> **学完本章你应该能**：(1) 解释 Zephyr 与 FreeRTOS 在设计哲学上的差别，(2) 看懂 Zephyr 项目的目录结构，(3) 知道一个 driver 在 Zephyr 里怎么"接进来"，(4) 在 QEMU 上跑 Zephyr 的 hello_world。

---

## 26.1 Zephyr 是什么

Zephyr 项目 2016 年由 Linux 基金会启动，目标：**做一个 Apache 2.0 协议的"小型 Linux 风格"RTOS**。今天 Intel、NXP、Nordic、Antmicro 等公司都重度投入。

特征：
- **设备树 (Device Tree)** 描述硬件 → 编译时生成 C 数据结构
- **Kconfig** 配置功能 → 与 Linux 内核完全一致的工具链
- **west** 工具管理多 repo、build、flash、debug —— 自家版 Cargo / Bazel
- **子系统化**：网络栈、文件系统、USB、BLE、传感器、显示 都是独立 subsystem
- **POSIX 兼容**子集：能跑很多原本写给 Linux 的代码
- **arch 抽象**：支持 ARM、RISC-V、x86、ARC、Xtensa、SPARC、POSIX (跑在 Linux 上做测试)

代价：内核 50+ KB，比 FreeRTOS 大 5–10 倍。**适合中高端 MCU (Cortex-M4 + 256 KB 起)**。

---

## 26.2 一个对比表

| 维度        | FreeRTOS                | Zephyr                            |
|-------------|--------------------------|-----------------------------------|
| 内核大小    | 5–10 KB                  | 50+ KB                            |
| 启动配置    | 头文件宏 + linker         | Kconfig + 设备树                   |
| 驱动模型    | 自己写 / SDK 各家         | 统一 Device API (`device_get_binding`) |
| 网络         | + lwIP                   | 自带 IPv4/6 + 6LoWPAN + Thread     |
| 文件系统     | 第三方                    | LittleFS / FatFS 集成               |
| BLE         | 第三方 / SDK              | 自带完整 BLE host + controller     |
| 测试        | 第三方                    | 自带 ztest + Twister              |
| 学习曲线     | 平                       | 陡（要先学 Kconfig + DT）           |

---

## 26.3 项目结构

一个最小 Zephyr 应用：

```
my_app/
├── CMakeLists.txt
├── prj.conf            ← 应用级 Kconfig 覆盖
├── boards/             ← 自定义板配置（可选）
│   └── my_board.overlay  ← 设备树 overlay
└── src/
    └── main.c
```

### main.c

```c
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

int main(void)
{
    printk("Hello from Zephyr!\n");
    while (1) {
        k_msleep(1000);
        printk("tick\n");
    }
    return 0;
}
```

### prj.conf

```
CONFIG_PRINTK=y
CONFIG_GPIO=y
CONFIG_THREAD_NAME=y
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(my_app)
target_sources(app PRIVATE src/main.c)
```

---

## 26.4 设备树：硬件描述与代码解耦

Zephyr 直接借用了 Linux 的设备树语法。每块板有一份 `.dts`：

```dts
/ {
    model = "QEMU Cortex-M3";
    chosen {
        zephyr,console = &uart0;
    };
    
    soc {
        uart0: uart@4000c000 {
            compatible = "ti,stellaris-uart";
            reg = <0x4000c000 0x1000>;
            interrupts = <5 3>;
            current-speed = <115200>;
            status = "okay";
        };
    };
};
```

代码里**通过 DT_NODELABEL / DEVICE_DT_GET 拿到设备**：

```c
const struct device *uart = DEVICE_DT_GET(DT_NODELABEL(uart0));
uart_poll_out(uart, 'H');
```

驱动代码完全不知道 UART 在 `0x4000C000` —— 一切由设备树决定。**这就是设备树的核心价值：硬件信息从代码中剥离**。

第 30 章讲 Linux 设备树时还会回到这。

---

## 26.5 内核 API 速览

线程、同步、定时和 FreeRTOS 几乎一对一映射，但 API 名字不同：

```c
K_THREAD_DEFINE(led_tid, 512, led_thread, NULL, NULL, NULL, 5, 0, 0);
/* 等同 FreeRTOS xTaskCreate */

K_SEM_DEFINE(my_sem, 0, 1);
k_sem_take(&my_sem, K_FOREVER);
k_sem_give(&my_sem);

K_MSGQ_DEFINE(my_q, sizeof(uint32_t), 16, 4);
k_msgq_put(&my_q, &val, K_NO_WAIT);
k_msgq_get(&my_q, &val, K_FOREVER);

k_mutex_init(&my_mutex);
k_mutex_lock(&my_mutex, K_FOREVER);
k_mutex_unlock(&my_mutex);
```

数据结构尽量编译期定义（`K_*_DEFINE`），避免动态分配。

---

## 26.6 在 QEMU 上跑 Zephyr hello_world

```bash
# 1. 装 west 和工具链
pip install west
west init zephyrproject && cd zephyrproject && west update

# 2. 装 Zephyr SDK (自动下载交叉工具链)
west zephyr-export
west sdk install

# 3. 跑 hello_world
cd zephyr
west build -p auto -b qemu_cortex_m3 samples/hello_world
west build -t run
```

输出：

```
*** Booting Zephyr OS build v3.x.0 ***
Hello World! qemu_cortex_m3
```

第一次安装较费时（~20 分钟）。但**装完后 west 就是你的全部工具** —— build、flash、debug、test。

---

## 26.7 Zephyr 子系统

| 子系统      | 干啥                              |
|-------------|-----------------------------------|
| **drivers** | 100+ 通用驱动（GPIO/I²C/SPI/UART/...） |
| **net**     | TCP/IP、CoAP、MQTT、LwM2M           |
| **bluetooth** | 完整 BLE host + LL                 |
| **fs**      | LittleFS、FAT、NVS                  |
| **shell**   | 串口 / Telnet 交互式 shell           |
| **logging** | 异步日志，多 backend                |
| **sensor**  | 统一 sensor API（DHT11 ↔ BMP180 同接口）|
| **usb**     | USB device stack（CDC/HID/MSC）     |
| **mgmt**    | OTA、设备管理协议 (MCUmgr)          |
| **storage** | 流式存储 / 镜像更新                  |

子系统化的好处：换硬件不改业务代码，只改 DT。

---

## 26.8 谁在用 Zephyr 真生产

- **Nordic Semiconductor**：nRF Connect SDK 的内核
- **NXP**：MCUXpresso for Zephyr
- **Espressif**：ESP32 在 Zephyr 上的支持
- **Google**：Pixel Watch 部分组件
- **Intel**：边缘 IoT 网关

行业趋势：新项目里 Zephyr 占比逐年上升，FreeRTOS 在小芯片守住主战场。

---

## 26.9 自检题

1. 为什么 Zephyr 选择继承 Linux 的设备树，而不是自创一套？
2. `K_THREAD_DEFINE` 与 `k_thread_create` 都能创建线程，差别？
3. Zephyr 的 `device_get_binding("UART_0")` 和 `DEVICE_DT_GET(DT_NODELABEL(uart0))` 哪个更现代？
4. 在 8-bit 8051 上跑 Zephyr 现实吗？

答案见 `code/answers.md`。

---

## 26.10 与后续章节的联系

| 概念             | 下游章节                                  |
|------------------|-------------------------------------------|
| 设备树           | [30 设备树](../30_设备树/)                  |
| Kconfig          | [29 交叉编译 + Buildroot](../29_交叉编译_Buildroot/) |
| 通用驱动 API     | [32 子系统驱动](../32_子系统驱动模型/)     |
| BLE host         | [23 无线协议](../23_无线协议入门/) 回顾    |

下一章 [27 实时性深入](../27_实时性深入/) 把"实时"这个词剖开，看 WCET、抖动、可调度性分析。
