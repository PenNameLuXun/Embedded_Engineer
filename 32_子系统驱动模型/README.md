# 第 32 章　子系统驱动模型：platform / I²C / SPI / GPIO

> 上一章我们用 `register_chrdev_region` 手工注册了字符设备。真实驱动几乎不这么写 —— 因为绝大多数硬件能套进一个**子系统**：platform device、I²C（Inter-Integrated Circuit，集成电路互联总线）client、SPI（Serial Peripheral Interface，串行外设接口）device、GPIO（General Purpose Input/Output，通用输入/输出）chip……子系统帮你把"硬件描述 → driver probe → 资源管理 → user 接口"全部串起来。这一章看子系统怎么工作。
>
> **学完本章你应该能**：(1) 解释 device / driver / bus 三件套，(2) 写一个 platform driver 框架，(3) 知道为什么不直接写 chrdev 而要走子系统，(4) 看到一份内核源码能猜出它属于哪个子系统。

---

![子系统驱动模型配图](images/device_driver_bus.png)

## 32.1 Linux 设备模型核心：device / driver / bus

```
   bus_type ────────────────────────────
       │                                │
       ├── device_register(dev)         ├── driver_register(drv)
       │                                │
       ↓                                ↓
   bus 上的 devices             bus 上的 drivers
       └─────── match(dev, drv) ────────┘
                     │
                 匹配成功
                     │
                drv->probe(dev)
```

![32.1 Linux 设备模型核心：device / driver / bus](images/generated/linux_device_driver_bus_direct.png)

每条 **bus** 维护两张表：device 表 + driver 表。**bus.match()** 决定怎么配对。

- **platform_bus**：CPU（Central Processing Unit，中央处理器）内部直挂的外设（UART、GPIO、I²C 控制器自己）。这类设备无法被自动发现，需要通过设备树或板级代码来描述，这正是 platform 总线模型的用途——用于无法自发现的设备
- **i2c_bus**：I²C 总线上的设备（EEPROM、传感器）
- **spi_bus**：SPI 总线上的设备
- **usb_bus**, **pci_bus**, **mmc_bus**（MMC，MultiMediaCard，多媒体卡存储接口）, **mdio_bus**, ...

写驱动时**你只需要关心：注册到哪条 bus + 实现 probe**。

> **为什么要有这个模型？** 想象没有子系统的世界：每个驱动都要自己写"发现设备 → 申请资源 → 清理资源"的完整流程，代码重复率极高，资源泄漏的 bug 到处都是。Linux 设备模型把这套流程标准化：设备和驱动各自注册到 bus，bus 负责撮合（match），撮合成功后统一调用 probe。就像婚介所——设备是"甲方"，驱动是"乙方"，bus 是"红娘"，双方都不需要主动找对方。

---

## 32.2 platform driver 模板

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/io.h>

static int my_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct resource *res;
    void __iomem *base;
    int irq;

    /* 1. 从 DT 拿 MMIO */
    res  = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    base = devm_ioremap_resource(dev, res);
    if (IS_ERR(base)) return PTR_ERR(base);

    /* 2. 从 DT 拿 IRQ（Interrupt ReQuest，中断请求）*/
    irq = platform_get_irq(pdev, 0);
    if (irq < 0) return irq;

    /* 3. 读自定义属性 */
    u32 rate;
    if (device_property_read_u32(dev, "sample-rate", &rate))
        rate = 48000;

    dev_info(dev, "probed: base=%p irq=%d rate=%u\n", base, irq, rate);
    return 0;
}

static const struct of_device_id my_of_match[] = {
    { .compatible = "vendor,my-thing" },
    { },
};
MODULE_DEVICE_TABLE(of, my_of_match);

static struct platform_driver my_driver = {
    .driver = {
        .name = "my-thing",
        .of_match_table = my_of_match,
    },
    .probe = my_probe,
};
module_platform_driver(my_driver);

MODULE_LICENSE("GPL");
```

**核心简化**：
- `module_platform_driver` 一行替代 `module_init/exit`
- `devm_*` 自动 unwind 资源
- DT 节点的 reg/interrupts 由框架解析、直接给你

写一个 platform driver 比手工 chrdev 少 80% 样板代码。

> **probe 函数是驱动的"入场仪式"**：当内核通过 compatible 字符串匹配到设备树节点和你的驱动时，它调用 probe 函数，把对应的 platform_device（设备描述）传进来。probe 里你申请资源、初始化硬件、注册到子系统。如果 probe 返回 0 表示成功，返回负数表示失败（内核会打印错误并不加载这个驱动实例）。**probe 失败不会崩溃，只会优雅地报告"驱动加载失败"。**

---

## 32.3 I²C client driver

挂在 I²C 总线上的设备（传感器、EEPROM）：

```c
#include <linux/i2c.h>

static int bmp280_probe(struct i2c_client *client)
{
    s32 id = i2c_smbus_read_byte_data(client, 0xD0);
    dev_info(&client->dev, "chip id = 0x%x\n", id);
    return 0;
}

static const struct i2c_device_id bmp280_id[] = {
    { "bmp280", 0 }, { }
};
MODULE_DEVICE_TABLE(i2c, bmp280_id);

static const struct of_device_id bmp280_of[] = {
    { .compatible = "bosch,bmp280" }, { }
};
MODULE_DEVICE_TABLE(of, bmp280_of);

static struct i2c_driver bmp280_drv = {
    .driver = {
        .name = "bmp280",
        .of_match_table = bmp280_of,
    },
    .probe = bmp280_probe,
    .id_table = bmp280_id,
};
module_i2c_driver(bmp280_drv);
```

I²C 子系统自动：分配 I²C client、调度总线访问、提供 `i2c_smbus_*` 高级 API。**你完全不用管 I²C 协议时序**。

SPI client driver 结构几乎一模一样，把 `i2c_` 换 `spi_`、`i2c_smbus_read` 换 `spi_write_then_read`。

> **I²C 子系统替你做了什么？** I²C 是一种两线串行总线（SCL 时钟线 + SDA 数据线），协议有严格的时序要求：START 条件、地址帧、ACK 应答、STOP 条件……如果手写这些时序代码，每个 I²C 传感器驱动都要重复实现，且容易出错。I²C 子系统把这些全封装好了，你只需调用 `i2c_smbus_read_byte_data(client, reg)` 就能读取寄存器，背后的时序由 I²C 控制器驱动处理。

---

## 32.4 GPIO 子系统

### 用 GPIO（消费方）

```c
struct gpio_desc *led = devm_gpiod_get(dev, "led", GPIOD_OUT_LOW);
gpiod_set_value(led, 1);
```

`devm_gpiod_get(dev, "led", ...)` 看 DT `led-gpios = <&gpio0 7 0>` 自动找到对应的 GPIO 控制器 + 第 7 脚 + 极性。**驱动代码完全不知道板子上 LED 是 GPIO0 还是 GPIO3**。

### 提供 GPIO（生产方，即写一个 GPIO 控制器驱动）

实现 `struct gpio_chip` + 注册：

```c
static int my_gpio_get(struct gpio_chip *chip, unsigned offset) { ... }
static void my_gpio_set(struct gpio_chip *chip, unsigned offset, int v) { ... }
static int my_gpio_dir_out(struct gpio_chip *chip, unsigned o, int v) { ... }
static int my_gpio_dir_in(struct gpio_chip *chip, unsigned o) { ... }

struct gpio_chip chip = {
    .label = "my-gpio",
    .ngpio = 32,
    .get   = my_gpio_get,
    .set   = my_gpio_set,
    .direction_input  = my_gpio_dir_in,
    .direction_output = my_gpio_dir_out,
};
devm_gpiochip_add_data(dev, &chip, my_state);
```

第三方驱动 `devm_gpiod_get` 就能用了。**子系统把"提供者"和"消费者"解耦**，这是 Linux 驱动模型的精髓。

---

## 32.5 其它常用子系统

| 子系统          | 用途                              | 关键 API                            |
|-----------------|-----------------------------------|-------------------------------------|
| clk             | 时钟树                              | `devm_clk_get`, `clk_prepare_enable` |
| reset           | 复位线                              | `devm_reset_control_get`            |
| regulator       | 电源域                              | `devm_regulator_get`, `enable`       |
| pinctrl         | 引脚复用                            | DT 自动                              |
| pwm             | PWM 输出                            | `devm_pwm_get`, `pwm_apply_state`    |
| iio             | IIO（Industrial I/O，Linux工业I/O子系统，统一ADC/传感器接口）| iio_dev |
| input           | 键盘 / 触摸屏                       | input_dev                            |
| v4l2            | V4L2（Video for Linux 2，Linux视频子系统框架）摄像头 | v4l2_dev              |
| drm             | 显示 (LCD)                          | drm_device                           |
| net_device      | 网卡                                | netif_*                              |
| mtd             | MTD（Memory Technology Device，内存技术设备，Linux中NAND/NOR Flash的抽象层）| mtd_info |
| crypto          | 加解密                              | crypto_alg                           |
| alsa            | ALSA（Advanced Linux Sound Architecture，高级Linux声音架构）| snd_card |

每个子系统都有自己的 maintainer、binding 文档（`Documentation/devicetree/bindings/`）、example 驱动。写驱动前**先找子系统**永远是对的。

---

## 32.6 子系统的好处再总结

1. **资源管理统一**：devm_ + bus 框架，错误处理几乎不会泄漏
2. **用户接口统一**：例如 GPIO 都通过 sysfs（内核向用户空间导出设备信息的虚拟文件系统）的 `/sys/class/gpio` 或 `gpiod_*` 暴露
3. **DT 接入统一**：`of_device_id` + 框架查 `compatible`
4. **跨架构可移植**：换 SoC（System on Chip，片上系统）只换 DT 不改驱动
5. **多个驱动共享 helper**：例如多家 I²C 控制器都用 `i2c-core` 提供的 SMBus 仿真

---

## 32.7 真实例子：怎么读源码

要看一个真实小驱动 LM75 (I²C 温度计)：

```bash
# 在 Linux 源码里
ls drivers/hwmon/lm75.c
ls Documentation/devicetree/bindings/hwmon/lm75.yaml
```

约 600 行 C + 50 行 binding。流程：
1. probe 时 i2c_smbus 读 chip ID → 验证
2. 注册到 hwmon 子系统：`devm_hwmon_device_register_with_groups`
3. hwmon 自动暴露 `/sys/class/hwmon/hwmon0/temp1_input` 等用户接口
4. 用户 `cat temp1_input` → hwmon → lm75 read → i2c read → 数据回来

整个链路你不写一行胶水。

> **读真实驱动的技巧**：看陌生驱动时先找 `module_xxx_driver()`（注册宏），确认它属于哪个子系统；再找 probe 函数，看它申请了哪些资源；最后看注册到哪个子系统（hwmon、input、v4l2...），这决定了用户接口在 `/sys/` 下的什么位置。这三步能让你快速看懂 90% 的 Linux 驱动代码。

---

## 32.8 自检题

1. 为什么 platform driver 比直接写 chrdev 好？
2. 一个驱动同时支持 I²C 和 SPI 两种接口（如 BMI160），怎么组织？
3. `devm_gpiod_get` 找不到 DT 里对应的 GPIO，会怎么样？
4. 同一个 SoC 上两个相同型号的 UART 控制器，驱动怎么区分？

答案见 `code/answers.md`。

---

## 32.9 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| sysfs / hwmon     | [33 用户态接口](../33_用户态接口/)         |
| ftrace + 子系统    | [34 调试与性能](../34_调试与性能/)         |
| 驱动签名          | [40 嵌入式安全](../40_嵌入式安全/)         |
| 驱动 OTA 更新       | [42 OTA](../42_OTA_固件升级/)              |

下一章 [33 用户态接口](../33_用户态接口/) 讲 sysfs、procfs、netlink、UIO 怎么把驱动暴露给用户程序。
