# 第 34 章自检题答案

1. (a) `top` / `htop` 看是不是某进程占满 CPU；(b) `cat /proc/interrupts` 看是不是中断风暴；(c) `dmesg | tail` 看驱动有没有异常打印；(d) `perf top` 找内核里热点函数。十之八九能定位。

2. **ftrace 跟特定函数 / 事件**（白盒，要知道函数名）—— 准确但需要先猜对。**perf 采样**（黑盒）—— 不需要先验知识，给一张"哪里最忙"的图。**实战流程**：perf 找热点 → ftrace 跟进具体函数行为。

3. Linux 内核仍有些**不可中断段**（如 spinlock 持有期间）。PREEMPT_RT 把绝大多数 spinlock 变成可睡眠 mutex 减小延迟，但 100 µs 仍比 Cortex-M RTOS 的 10 µs 高一个量级。**硬实时 ≤ 10 µs 要求**只有 RTOS / 裸机 / 双核异构能满足。

4. (a) **动态注入**：不需要重 build 内核，运行时 attach 探针；(b) **图灵完备**（受限于安全 verifier）：能在内核里跑 map / aggregate / 过滤；(c) **生产可用**：经过沙箱验证，不会让内核崩溃；(d) **跨内核版本可移植** (CO-RE)。ftrace 加 set_filter 仍是字符串过滤 + 简单 trace，bpftrace 能做近乎任意聚合统计。
