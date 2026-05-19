# 第 09 章 自检题答案

1. `0x0000_0000` 是 **初始 MSP**（栈顶）。`0x0000_0004` 是 **Reset_Handler 的地址**（最低位置 1 表示 Thumb 状态）。

2. `.data` 的"运行地址 (VMA)"在 SRAM —— 因为运行时要读写。  
   "装载地址 (LMA)"在 Flash —— 因为掉电要保住初值。  
   启动时 `Reset_Handler` 把 LMA → VMA 搬一次，之后 CPU 看到的就是 SRAM 上的可写副本。

3. `--gc-sections` 会删掉"看上去没被任何符号引用"的 section。向量表里那些 handler 没人显式 `bl`，只是被 CPU 硬件按地址读 → 链接器以为没人用。`KEEP()` 告诉它"别动这个"。

4. 通常 = `ORIGIN(SRAM) + LENGTH(SRAM)`，即 SRAM 的最末。因为 Cortex-M 的栈向下增长 (full descending)，从最高地址往低地址递减。

5. 因为 `Default_Handler` 用 `.weak`/`.thumb_set` 写成弱别名。GNU `ld` 在解析符号时：用户 C 代码里的 `SysTick_Handler` 是强符号 → 覆盖弱符号。两个强符号同名会报重定义错。
