# 第 19 章自检题答案

1. **被动响应模型** 让设备硬件大幅简化：不需要总线仲裁、不需要主动发起、不需要复杂调度。**Host 决定一切**。代价是设备延迟取决于 Host 轮询频率（Interrupt EP 由 Host 周期性 IN 查询）。

2. 从 USB-IF 申请 VID（年费约 $5000，或购买一次性 $4000 的 USB-IF non-logo VID）。小批量原型可用 **Microchip / FTDI 等芯片厂提供的子 VID/PID**（在它们的 USB-IF 注册下分配）。完全自用的内部产品可以乱填，但商业发布违反协议会被拒绝认证。

3. 音频 / 视频流要求**带宽预约 + 实时性**，丢一帧没事，**不能晚到**。Bulk 没有定时保证，可能因为别的设备占用 Bulk 带宽而被推迟。Isochronous 占预约带宽 + 不重传 = 完美匹配音视频的语义。

4. **Mass Storage Class (0x08)**，子类用 SCSI 透明命令集 (0x06)，协议 BBB (Bulk-Only Transport, 0x50)。再加一个块设备 backend（内部 Flash / SD 卡）就成 U 盘。
