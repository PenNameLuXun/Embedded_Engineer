# 第 30 章自检题答案

1. **不会自动得到** —— 驱动要主动 `of_property_read_u32`。改 DTS → 重 build DTB → 烧到目标 → 重启 → 内核解析新 DTB → 驱动 probe 时读到新值。**没有"自动同步"魔法**。

2. (a) 字符串可读、可 grep、跨平台不冲突；(b) 多个 vendor 各自管理命名空间不会撞 ID；(c) "兼容列表"用字符串数组天然表达（`compatible = "vendor,new", "vendor,fallback";` 允许驱动按从新到老顺序匹配）。

3. **改 DTS 适合**：板级硬件信息（电源、时钟、SoC 内置外设）—— 这些是固化的。**Overlay 适合**：扩展板 / hat / 用户加装的可选模块（树莓派加 SPI 屏幕）—— 不要污染主 DT。原则：**OEM 改 DTS，用户用 Overlay**。

4. **devm_** = device managed。注册时和 device 关联，**device unbind 时自动释放**。普通 `request_irq` 等如果忘 `free_irq` → 内存 / IRQ 泄漏。`devm_` 让 probe 失败回滚 / 模块卸载清理"自动做对"，大幅减少错误代码路径。
