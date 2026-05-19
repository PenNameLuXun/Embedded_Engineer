# 第 32 章自检题答案

1. **样板代码少 80%**：DT 自动 probe、devm 自动回滚、bus 自动管理设备生命周期、与电源 / 时钟 / 复位等子系统天然集成。手工 chrdev 写到能跑稳定生产质量，要补 power management、设备热插拔、user permission 等，最终代码量比 platform 大很多倍。

2. 把核心逻辑放在 `bmi160-core.c` 写成 regmap-based 驱动（提供 read/write 抽象）。再写 `bmi160-i2c.c` 和 `bmi160-spi.c` 各自负责 regmap 初始化，把 regmap 传给 core probe。Linux 大量传感器驱动都是这种 "core + bus" 拆分。

3. 返回 `ERR_PTR(-ENOENT)`。`IS_ERR()` 必查。如果 GPIO 是可选的（如 reset 引脚），可以用 `devm_gpiod_get_optional` —— 没配置时返回 NULL 而不是错。

4. DT 里两个独立节点：`uart0: serial@4000c000` 和 `uart1: serial@4000d000`，各自有 `reg` 和 `interrupts`。Linux 内核 probe 时给每个节点实例化一个 device，调用 probe 时通过 `dev_name(dev)` 或 `pdev->id` 区分。**实例化数据存在 `platform_set_drvdata`**，不要用全局静态变量。
