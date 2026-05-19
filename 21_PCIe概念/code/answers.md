# 第 21 章自检题答案

1. CPU 读 DRAM 经过 L1/L2/L3 + 控制器，命中 cache 几 ns，未命中 ~80 ns。CPU 读 PCIe 设备 BAR：TLP 走 Root Complex → 设备 → 回 Completion → RC → CPU。**通常 500 ns ~ 2 µs**，比 DRAM 慢 1–2 个数量级。所以驱动写代码时尽量 **批写、避免读返回值**（读会卡 CPU 等 completion）。

2. 不是。**BAR 写进的是"我要的大小"**：固件先往 BAR 写全 1，再读回看哪些位变 0 → 推算尺寸 → 在系统地址空间挑一块够大的物理地址 → 写进 BAR。**这套枚举由 BIOS/UEFI 或 Linux PCI 子系统做**，驱动看到的是已分配好的地址。

3. INTx 多个设备共享一根中断线，CPU 中断后要查询每个设备的 status reg 确认是谁触发 → 慢且容易丢。MSI 每个设备每个 vector 独立，**直接路由到具体 CPU 核**，配合 IRQ affinity 实现负载均衡。

4. **RC (Root Complex)**：连接 CPU 内存控制器到 PCIe 拓扑，相当于"根路由器"。  
   **Switch**：内部带多个 port，转发 TLP，扩展拓扑。  
   **Endpoint**：真正的设备（显卡、SSD），既不转发也不挂下游。
