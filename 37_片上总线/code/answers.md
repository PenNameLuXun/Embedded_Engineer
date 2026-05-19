# 第 37 章自检题答案

1. (a) 性能-成本权衡：AXI IP 比 APB 大 10–20×，全 AXI 浪费面积；(b) UART/GPIO 这种低速外设跑 AXI 没意义（带宽 < 1 MB/s）；(c) 时序收敛：AXI 时钟通常 > 500 MHz，APB 100 MHz 就够，硬把 UART 拉到 500 MHz 物理实现极难；(d) 工程化：APB 接口简单，第三方 IP 选 APB 接入容易。

2. 完全可以。AXI 五通道全独立，read（AR + R）和 write（AW + W + B）可以在同一拍各自握手，完全并行 / 完全独立、不互相阻塞。这是 AXI 比 AHB 快的核心原因。

3. 会形成组合回路：`ready ← valid_to_ready_logic ← valid` 而 valid 又通过组合路径影响其它信号 → 综合工具看到 0-延迟环，仿真 / 综合不一致。AXI 协议明文禁止。**ready 必须独立于 valid 的当拍状态**。

4. APB 协议允许 PREADY 长时间不拉高（叫"wait state"），master 必须等。所以**长拉伸合法但浪费 master 周期**。设计上应尽量保证 PREADY 在 1-2 周期内完成；只有访问外部慢介质（如外部 SPI Flash）时合理。
