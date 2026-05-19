# 第 33 章自检题答案

1. 用十六进制字符串：`echo "AA:BB:CC:DD:EE:FF" > mac_addr`，内核侧用 `mac_pton(buf, mac)` 解析。**保持一行文本** = sysfs 风格。若必须二进制就改用 ioctl 或 sysfs `*_bin_attribute` (二进制 attr，能 mmap)。

2. **uevent** 来自内核（设备插拔、状态变化），netlink 推送；**inotify** 是文件系统级事件（文件 created/modified/deleted）。前者监控硬件，后者监控数据。两者完全独立，常一起用：udev 收 uevent 创建 /dev 节点；应用收 inotify 知道配置文件改了重新加载。

3. 内核 ISR 里调 `uio_event_notify(info)`：增加内部 event 计数器，唤醒等在 read 上的用户进程。用户 read 返回当前 event count；用户可以比较两次 read 值检测错过的中断。**用户必须主动 read，否则中断"积压"——计数器涨但不通知**。这是 UIO 接口的核心同步机制。

4. ABI 一旦设计了，**永远兼容**。新加字段不能改既有结构体大小（必须用 `_IO/_IOWR` magic + size 编码 + 分新命令号）。Linux 历史上不少子系统因 ioctl 设计失误维护成本爆炸（KVM 的初版、早期 V4L1 → V4L2 大重写）。原则：(a) 结构体加 reserved + flags 字段；(b) 大小变了用新 cmd；(c) 跨 32/64 位测试。
