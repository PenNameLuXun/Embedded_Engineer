# 第 28 章自检题答案

1. BootROM 跑在芯片内部 SRAM 上（~几十 KB），太小装不下完整 U-Boot + DDR 初始化代码。所以 BootROM 只装"裸命"那部分（极小的 SPL loader），把 SPL 拷到 SRAM 跑 → SPL 初始化 DDR → 把 U-Boot 从存储加载到 DDR 跑。SoC 集成度越高、SRAM 越大，SPL 越能省略（部分高端 SoC 直接跳过 SPL）。

2. 内核启动时把 console 重定向到 ttyAMA1（第二个 PL011 UART）。如果板子上 ttyAMA0 是引出来的调试口而 ttyAMA1 没接 → **dmesg 看不到，看起来挂了，其实正常跑**。这是入门级"启动神秘失败"的经典踩坑点。

3. initramfs 是**只在启动早期使用**的 RAM 盘根文件系统。内核解压它 → 跑 `/init` → 它做一些前期工作（mount 真根、解密、加载 module）→ `switch_root` 切到真根 → 释放 initramfs 内存。嵌入式很多情况下 initramfs 直接就是最终根（不切换）。

4. busybox init。资源占用差 100×（10 KB vs 几 MB）；启动快 5–10×；功能够 IoT 网关用。systemd 的依赖管理、socket activation 对家用 IoT 没价值。Yocto/桌面 Linux 才考虑 systemd。
