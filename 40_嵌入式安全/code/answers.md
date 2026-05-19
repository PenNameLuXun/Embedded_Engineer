# 第 40 章自检题答案

1. 几百毫秒到一两秒。RSA-2048 验签在 Cortex-M4 @ 168 MHz 软件实现约 200-500 ms；ECC-P256 约 50-100 ms；ECC-Ed25519 ~20 ms。有硬件加速器后 ECC < 10 ms，可以忽略。**Secure Boot 链路 < 1 秒** 是工业典型目标。

2. **硬件总线层面被拦截**：non-secure master 发起对 secure 内存地址的访问，TZ-M 的 SAU/IDAU 单元检查 → 返回 SecureFault 异常给 non-secure 世界。secure 数据从不出现在 non-secure 总线上。

3. (a) Flash 里加密的密钥必须用别的密钥解密，那个 master key 还是要存在哪 → 鸡生蛋。SE 把 master key 烧在硅片内的安全存储，**只用不读**。(b) SE 自身抗物理攻击 (mesh、自毁、防探针)，普通 Flash 一拆封装就读出来了。(c) 私钥**永远不离开 SE 芯片**，签名 / 加密都在 SE 内做，对外只暴露结果。

4. CPU 跑 `cmp r0, #0; bne fail`，攻击者在 `bne` 那一拍给 VCC 加一个尖刺，让 CPU 取错指令或执行错误，**分支被跳过** → 进入 secure 区。所以严肃安全代码**双重检查**关键判断：`if (auth()) ... else lockup(); ... if (!authed_again) lockup();`，让单次故障注入不够。
