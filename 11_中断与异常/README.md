# 第 11 章　中断与异常

> 上一章 echo 程序里，main 一直在死循环里轮询 UART —— **CPU 100% 占用却 99% 时间在等**。这是嵌入式工程师入门的第一个真正要解决的问题。这一章把"轮询"换成"中断"，CPU 才能去干别的事。
>
> **学完本章你应该能**：(1) 解释中断和异常的差别、Cortex-M 异常进出流程，(2) 写一个 UART RX 中断处理，(3) 处理 ISR 与主程序共享状态的同步问题，(4) 知道什么是中断延迟、为什么 ISR 要尽可能短。

---

## 11.1 中断 vs 异常 vs 故障

- **异常 (Exception)**：CPU 因为内部原因被打断（除零、非法指令、SVC 调用）。
- **中断 (Interrupt / IRQ)**：CPU 因为外部事件被打断（UART 收到字节、定时器到期、引脚电平变化）。
- **故障 (Fault)**：异常的子集，特指出错型（HardFault、BusFault、UsageFault、MemManage）。

在 Cortex-M 里，三者**走的是同一套机制 + 同一张向量表**，只是优先级不同。这就是为什么第 09 章那张向量表里 16 + 240 个槽位混在一起。

---

## 11.2 进入中断时硬件做的事（再走一遍）

第 08 章预告过，这里展开：

1. 当前正在执行的指令做完。
2. 把 8 个寄存器自动压栈：xPSR、PC、LR、R12、R3、R2、R1、R0 —— 这叫 **stacking**。
3. LR 写入一个特殊的 **EXC_RETURN** 值（0xFFFF_FFFx），表示"我是从异常返回的"。
4. 加载新的 PC = 向量表对应槽位的值，开始执行 ISR。
5. 进入 Handler 模式。

退出 ISR 时，CPU 看到 PC 跳到 EXC_RETURN（最低位置 1 + 高位特殊编码），**反向**做一遍：弹出 8 个寄存器，恢复模式，回到原指令的下一条。

**关键事实**：
- R0–R3 / R12 由硬件保护 → ISR 用它们写 C 代码不会破坏被打断的主程序状态。
- R4–R11 由编译器在 ISR 入口处 `push {r4-r7, ...}` 自动保护。
- 你不需要写一行汇编 ISR 包装。**直接拿 C 函数当 ISR**。

```c
void UART0_IRQHandler(void)
{
    /* 标准 C，任意指令、任意数据访问 */
}
```

只要名字在启动文件里被 `.weak` 别名指向 `Default_Handler`，C 里同名函数自动 override。

---

## 11.3 NVIC：让 IRQ 真的"通"过来

外设触发 IRQ 后，还需要满足三件事才能真打到 CPU：

1. 外设内部"中断使能"开了（如 UART 的 `IM` 寄存器）。
2. NVIC 里这个 IRQ 编号被使能（`NVIC_ISER`）。
3. CPU 的全局中断使能开着（`PRIMASK = 0`，即 `__enable_irq()`）。

少一条它就憋着不动。**新手 90% 的"中断没进"问题**都是这三个之一。

### NVIC API (CMSIS)

```c
NVIC_SetPriority(UART0_IRQn, 2);   /* 数字越小优先级越高 */
NVIC_EnableIRQ(UART0_IRQn);
__enable_irq();                     /* 全局开 */
```

LM3S6965 上 UART0 是 IRQ 5。CMSIS 头会给个 enum：

```c
typedef enum {
    GPIOA_IRQn = 0,
    /* ... */
    UART0_IRQn = 5,
    /* ... */
    SysTick_IRQn = -1,
} IRQn_Type;
```

负数 IRQn 是系统异常（SysTick、SVC、PendSV），正数才是外设。**`SysTick_IRQn = -1`**，所以你不会在 `NVIC_EnableIRQ` 里看到它，SysTick 由 `SYST_CSR.TICKINT` 自己使能。

---

## 11.4 在 echo 程序里加 UART RX 中断

复用第 10 章的项目，只改三个地方：

### ① UART 端开中断
```c
/* uart.c — 新增 */
void uart0_enable_rx_irq(void)
{
    /* IM 寄存器 bit 4 = RXIM (RX 中断屏蔽，写 1 = 不屏蔽) */
    UART0_IM |= (1u << 4);
}
```

### ② NVIC 端使能
```c
/* main.c */
#define UART0_IRQ_NUM   5

static void nvic_enable(int irq_num, int prio)
{
    /* 写优先级寄存器（每个 IRQ 占 8 bit） */
    *((volatile uint8_t *)(0xE000E400u + irq_num)) = (uint8_t)(prio << 5);  /* 取 3 高位 */
    /* 使能 IRQ */
    *((volatile uint32_t *)(0xE000E100u + (irq_num / 32) * 4)) = (1u << (irq_num & 31));
}
```

### ③ 写 ISR
```c
/* main.c */
volatile uint8_t  rx_buf[64];
volatile uint8_t  rx_head = 0, rx_tail = 0;

void UART0_IRQHandler(void)
{
    /* 1. 清外设中断标志 */
    UART0_ICR = (1u << 4);   /* RXIC */

    /* 2. 读所有可读字节进 ring buffer */
    while ((UART0_FR & UART0_FR_RXFE) == 0) {
        uint8_t c = (uint8_t)(UART0_DR & 0xFFu);
        uint8_t next = (rx_head + 1) % sizeof(rx_buf);
        if (next != rx_tail) {           /* 不溢出 */
            rx_buf[rx_head] = c;
            rx_head = next;
        }
    }
}
```

### ④ main 改成消费 ring buffer
```c
int main(void)
{
    led_init();
    uart0_init(50000000u, 115200u);
    uart0_enable_rx_irq();
    nvic_enable(UART0_IRQ_NUM, 2);

    int led = 0, n = 0;
    while (1) {
        /* 没事就 WFI 睡觉，节能 */
        if (rx_tail == rx_head) {
            __asm__("wfi");
            continue;
        }
        uint8_t c = rx_buf[rx_tail];
        rx_tail = (rx_tail + 1) % sizeof(rx_buf);
        uart0_putc((char)c);
        if (c == '\r') uart0_putc('\n');
        if (++n % 8 == 0) { led ^= 1; led_set(led); }
    }
}
```

**完整代码在 `code/04_irq_echo/`**。`make run` 跑。

---

## 11.5 ring buffer + ISR 的同步问题

上面那段 ring buffer：head 由 ISR 写，tail 由 main 写，**双方都读对方的指针**。这是经典的 **SPSC (single-producer single-consumer)** 队列。

| 谁     | 写哪个 | 读哪个              |
|--------|--------|---------------------|
| ISR    | head   | tail（判断是否满）  |
| main   | tail   | head（判断是否空）  |

只要：
- 这两个指针对齐 + 32 位（写本身原子）
- 用 `volatile`（避免编译器优化掉）
- **顺序**：ISR 必须 **先写 buf[head]，后更新 head**；main 必须 **先读 buf[tail]，后更新 tail**

就能 **无锁** 安全使用，不需要关中断。这是嵌入式高频姿势。多生产者 / 多消费者就需要锁或 LDREX/STREX 了。

---

## 11.6 关中断 / 临界区

有时实在没办法用无锁，得短暂关中断：

```c
uint32_t primask = __get_PRIMASK();
__disable_irq();
/* ---- 临界区 ---- */
__set_PRIMASK(primask);     /* 恢复之前的状态，注意不是无脑 enable */
```

或 CMSIS 等价宏。**保存并恢复**而不是无脑 enable，因为你可能本来就在更外层临界区里。

**代价**：临界区里所有 IRQ 都不会进入。直接拉高最坏中断延迟 → 影响实时性。**临界区要尽可能短**，几行汇编以内。

### `BASEPRI`：更精细的方法（ARMv7-M+）

`__disable_irq` 关所有 IRQ（除 NMI/HardFault）。**`BASEPRI`** 只屏蔽优先级**数字大于等于** N 的，比 N 小（更高优先级）的还能进：

```c
__set_BASEPRI(0x40);   /* 屏蔽优先级 ≥ 2 的中断（假设 8 级优先级） */
/* ... */
__set_BASEPRI(0);      /* 全开 */
```

FreeRTOS 就用这套机制实现 "FromISR" 系列 API 安全调用。第 25 章详述。

---

## 11.7 中断延迟与优先级

**中断延迟 (Interrupt Latency)** = 中断信号产生 → ISR 第一条指令执行之间的周期数。

Cortex-M3 在最理想情况下 **12 个时钟周期**：
- 当前指令完成 (最多 ~7 cycle 看指令)
- stacking 8 个寄存器 (8 cycle，但 Cortex-M 提供 zero-jitter 入口优化)
- 取向量、跳目标

什么会拉长？
- 你正好处于一段没法被打断的操作（LDM/STM 多寄存器装入）
- 高优先级中断把低优先级中断推后
- 临界区屏蔽
- Cache miss（M7 才会有）

### 优先级分组与抢占

Cortex-M3 / M4 实际优先级位数由厂商定，常见 3–4 bit。8 位优先级寄存器中：

```
| 抢占优先级 |   亚优先级    |
| <-- AIRCR.PRIGROUP 分割 --> |
```

- 抢占优先级：决定能不能打断当前 ISR
- 亚优先级：同抢占优先级时谁先跑

裸机基本不用区分，全用 4-bit 抢占就够；RTOS 才需要细分。

---

## 11.8 ISR 设计原则（必须背）

1. **ISR 越短越好** —— 几十微秒以内。复杂工作搬到 main / 任务里。
2. **不要在 ISR 里 `printf`、`malloc`、忙等长延时**。
3. **共享数据用 `volatile` + 原子 + ring buffer / 信号量**。
4. **清外设中断标志位**（写 `ICR` 之类），否则 ISR 退出后立刻又被叫一遍 → 死循环。
5. **优先级要规划**：高速 / 实时性强的中断 (DMA done、Timer overflow) 给高优先级；UART RX 中等；GPIO 边沿一般低。

---

## 11.9 SysTick 中断：复习

`SysTick_Handler` 是 ARM 标准异常，**不在 NVIC 控制下**，由 `SYST_CSR.TICKINT` 直接开。

```c
SysTick->LOAD = (50000000u / 1000u) - 1u;   /* 1 ms 节拍 */
SysTick->VAL  = 0;
SysTick->CTRL = 0x7;     /* CLKSOURCE=CPU | TICKINT | ENABLE */
```

```c
volatile uint32_t ticks;
void SysTick_Handler(void) { ticks++; }
```

下一章 12 详细玩。

---

## 11.10 自检题

1. 为什么 ISR 用 C 写就够，不需要写汇编"包装函数"？
2. 一个 IRQ 始终没进 ISR，应当检查哪三件事？
3. 一个 ISR 每次进入都 lockup 不返回，最可能是什么原因？
4. SPSC ring buffer 不需要锁的前提是什么？
5. `__disable_irq` 和 `BASEPRI` 的区别？什么时候用哪个？

答案见 `code/answers.md`。

---

## 11.11 与后续章节的联系

| 概念                | 下游章节                                          |
|---------------------|---------------------------------------------------|
| SysTick / 时基       | [12 定时器与 SysTick](../12_定时器与SysTick/)      |
| DMA 完成中断         | [13 DMA](../13_DMA/)                              |
| ISR 内 OS API        | [25 FreeRTOS 实战](../25_FreeRTOS实战/)            |
| 中断延迟 / 抖动      | [27 实时性深入](../27_实时性深入/)                  |

下一章 [12 定时器与 SysTick](../12_定时器与SysTick/) 在 ISR 基础上构建精准时基和 PWM 输出。
