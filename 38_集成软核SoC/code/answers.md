# 第 38 章自检题答案

1. **100 MHz 软核在 FPGA 上算典型**。硬核 ASIC 能跑 GHz 是因为：(a) 物理工艺 7nm/5nm，门延迟 ps 级；(b) ASIC 标准单元手工优化；(c) Clock tree、Power grid 全定制。FPGA 的 LUT + 通用路由有寄生电容和延迟，~150 MHz 是大多数低端 FPGA 的极限。高端 FPGA (UltraScale+/Stratix 10) 能到 500 MHz+ 但价格陡。

2. **AXI 互连内置仲裁器**：通常 round-robin 或加权优先级。两个 master 同拍发起，互连让一个先通过 → 另一个 valid 维持等下拍。延迟会增加但功能正确。

3. (a) **实时性差**：Cortex-A 大 cache + 乱序 → 抖动大；(b) **功耗高**：跑 GHz 主频 + cache 一直转；(c) **不安全**：跑 Linux 内核数百万行代码，攻击面太大。Cortex-R / M 各司其职更合理。

4. 能，但需要 (a) MMU（VexRiscv 加 MMU 选项）；(b) Cache（D-Cache + I-Cache）；(c) 足够 DRAM（~32 MB+）；(d) 必备外设 (UART/Timer/PLIC)。开源软核能跑 Linux 的例子：VexRiscv + LiteX 在 ECP5 FPGA 上 ~80 MHz 跑 Buildroot Linux。
