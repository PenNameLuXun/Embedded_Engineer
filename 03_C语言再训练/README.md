# 第 03 章　C 语言再训练（嵌入式视角）

> 你会写 C。但"会写"和"在 MCU 上不踩坑地写"之间，隔着一整套关于 **内存布局、链接、`volatile`、对齐、原子性** 的细节。这一章把这些细节集中讲清楚。
>
> **学完本章你应该能**：(1) 画出一个嵌入式程序的内存布局，(2) 解释为什么外设地址必须 `volatile`，为什么共享变量也得，(3) 知道哪些 C 操作不是原子的、在 ISR 里要怎么处理，(4) 看到 `struct` 能立刻估出它的 `sizeof`。

---

## 3.1 一个嵌入式 C 程序的"全景"

```
       ┌─────────────────────────────┐  0xFFFF_FFFF
       │  外设寄存器 (Peripheral)    │
       ├─────────────────────────────┤
       │  …                          │
       ├─────────────────────────────┤
       │  Stack ↓ (向下增长)          │
       │                             │
       │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─       │
       │                             │
       │  Heap ↑ (向上增长，若使用)   │
       ├─────────────────────────────┤
       │  .bss  (未初始化全局/static) │  RAM 区
       ├─────────────────────────────┤
       │  .data (已初始化全局/static) │
       ├─────────────────────────────┤
       │  …                          │
       ├═════════════════════════════┤
       │  .rodata (常量、字符串字面量)│  Flash 区
       ├─────────────────────────────┤
       │  .text   (代码)              │
       ├─────────────────────────────┤
       │  中断向量表                  │
       └─────────────────────────────┘  0x0000_0000
```

**关键事实**：
- `.text` / `.rodata` 放在 **Flash**（不可写，掉电不丢）。
- `.data` / `.bss` / Stack / Heap 放在 **SRAM**。
- `.data` 的初值住在 Flash，启动时由启动文件搬到 SRAM。这是为什么"加电后全局变量就是你写的初值"的真正机制。
- `.bss` 是"未初始化或初始化为 0"的全局，启动时清零。

第 09 章 [启动文件与链接脚本](../09_启动文件与链接脚本/) 会把这一切落到 `ld` 脚本上。

---

## 3.2 五种存储期 (Storage Duration)

C 标准把变量按生存期分五类，每类对应上图不同区域：

| 关键字 / 位置          | 例子                          | 区域       | 生存期               |
|-------------------------|-------------------------------|------------|----------------------|
| 全局 / `static` 文件域 | `int g_counter = 0;`         | `.data` / `.bss` | 程序整生命周期      |
| 函数内 `static`         | `void f() { static int s; }` | `.data` / `.bss` | 程序整生命周期      |
| `const` 全局            | `const char *s = "hi";`      | `.rodata`  | 程序整生命周期      |
| 局部自动 `auto`         | `void f() { int x; }`        | Stack      | 函数调用期间        |
| `malloc`                | `p = malloc(64);`             | Heap       | 直到 `free`         |

**嵌入式高频规则**：
- 尽量用静态分配，少用 heap。MCU 上 heap fragmentation 很难调，FreeRTOS 也常用静态 task 创建。
- 大缓冲（>1 KB）放 `static`，别在栈里，避免 stack overflow（栈通常只有几 KB）。
- 中断处理函数 / 任务函数里不要 `malloc`。

---

## 3.3 指针：再过一次

### 指针运算的单位是"被指类型"

```c
int   *p = (int*)0x1000;
char  *q = (char*)0x1000;
p++;   /* p == 0x1004，前进 sizeof(int)=4 字节 */
q++;   /* q == 0x1001，前进 1 字节 */
```

这套规则在指针强转访问外设寄存器时非常重要。

### 指针 vs 数组

```c
int a[10];
int *p = a;            /* 数组名"退化"为指向首元素的指针 */
a[3]  == *(a+3)        /* 等价 */
sizeof(a) == 40        /* 整个数组 */
sizeof(p) == 4 或 8    /* 仅是一个指针 */
```

函数参数里的 `int a[10]` **不真的是数组**，会被改成 `int *a`。所以 `sizeof(a)` 在函数里没法拿到长度。这就是 `len` 参数必须分开传的原因。

### 函数指针 = ISR 表的本质

```c
typedef void (*isr_t)(void);

isr_t vector_table[] = {
    reset_handler,
    nmi_handler,
    hardfault_handler,
    /* ... */
};
```

中断向量表就是一张函数指针数组。CPU 触发异常时硬件自动从这张表里加载对应槽位的地址跳过去。第 09 章详述。

---

## 3.4 `volatile`：把编译器的优化关掉

编译器默认假设"内存只在我看得见的地方变"。**`volatile`** 告诉它："这个变量我不保证什么时候会变 / 变了别人会看，请每次都老老实实读 / 写。"

### 必须 `volatile` 的三种场景

#### ① 外设寄存器（MMIO）

```c
#define UART_DR (*(volatile uint32_t *)0x4000C000)

while ((UART_FR & TXFE) == 0) ;   /* 等 FIFO 空 */
UART_DR = 'A';
```

如果不加 `volatile`，编译器看到循环里 `UART_FR` 不变就把读优化成一次 → 死循环。

#### ② ISR 和主程序共享的变量

```c
volatile uint8_t flag;

void TIM_IRQHandler(void) { flag = 1; }

int main(void) {
    while (!flag) ;   /* 等中断把 flag 改成 1 */
}
```

不加 `volatile`，编译器看主循环里 `flag` 没被改就把读提到循环外 → 死等。

#### ③ 多核共享内存 / DMA buffer

DMA 写完缓冲，CPU 这边要看到新值。光 `volatile` **不够**，还得加 cache invalidate / memory barrier。但 `volatile` 是必要条件之一。

### `volatile` 不解决什么

- 不保证 **原子性**（见 §3.7）
- 不是 **内存屏障**（见 §3.8）
- 不阻止 **CPU 的乱序执行 / 推测**

简言之：`volatile` 只针对**编译器**，不针对 CPU。

---

## 3.5 `const` / `static` / `extern`：链接的三件套

| 关键字     | 在文件作用域       | 在函数内              |
|------------|--------------------|-----------------------|
| `static`   | 仅本文件可见（内部链接） | 静态存储期变量      |
| `extern`   | 声明外部定义        | 同上                  |
| 无         | 全局符号（外部链接） | 自动存储期            |

`static` 函数变量 + 文件作用域 `static` 是模块化封装的基石。看到 `static int xxx` 在文件顶部，等价于其它语言里的 `private` / `module-local`。

`const` 配合 `static`：

```c
static const char banner[] = "MyDevice v1.0";
```

放 `.rodata`（Flash），不占 RAM，写它会触发 fault。

---

## 3.6 `struct` 对齐与紧凑布局

### 默认对齐

每个字段从满足它自身对齐要求的最近地址开始；整个 struct 的大小也对齐到最大字段。

```c
struct {
    uint8_t  a;       // off 0
    /* 3 padding */
    uint32_t b;       // off 4
    uint16_t c;       // off 8
    uint8_t  d;       // off 10
    /* 1 padding */
};                    // sizeof = 12, align = 4
```

### 影响 `sizeof` 的两件事

- 字段顺序（按大小降序排能省 padding）
- 编译器选项（`-fpack-struct`）

### `__attribute__((packed))`

完全去掉 padding：

```c
struct __attribute__((packed)) frame {
    uint8_t  type;
    uint32_t length;   // 紧贴 type，offset 1，非对齐！
    uint8_t  payload[64];
};
```

**用途**：解析网络/总线协议头，字段必须严格按规范紧凑。

**风险**：`frame->length` 在 ARMv6-M (Cortex-M0) 上访问非对齐字会 HardFault。在 Cortex-M3+ 上慢一点但能跑。安全做法：
```c
uint32_t len;
memcpy(&len, &f->length, sizeof(len));
```
`memcpy` 编译器会拆成字节访问，肯定不会非对齐。

### 位域 (Bit-field)

```c
struct ctrl_reg {
    uint32_t enable     : 1;
    uint32_t mode       : 3;
    uint32_t reserved   : 4;
    uint32_t prescaler  : 8;
    uint32_t            : 16;   /* 匿名占位 */
};
```

**警告**：位域的位排列顺序、底层类型选择是 **实现定义** 的，不同编译器可能不同。**严肃工业代码很少用位域映射外设**，更稳的做法是用 `volatile uint32_t` + 移位掩码（见第 01 章 §1.3）。位域用来描述协议帧倒是常见。

---

## 3.7 原子性：什么操作能"一气呵成"

ISR 和主程序共享变量时，最容易踩的坑：

```c
volatile uint32_t counter;

void main(void) {
    counter++;          // 看似一条，其实三步
}
```

`counter++` 在 ARM 上被编译成：
```
LDR r1, [r0]    ; r1 = counter
ADD r1, r1, #1
STR r1, [r0]    ; counter = r1
```

中间任何一步被中断打断 → 中断里也改了 `counter` → 数据 **lost update**。

### 哪些是原子的？

ARMv7-M / RV32：
- 对齐的单字读 / 写（32 位）：**原子**
- 对齐的半字 / 字节读 / 写：**原子**
- `i++` / `i += x` / `i &= mask` 等读-改-写：**非原子**
- 多字节结构访问：**非原子**

### 怎么办？

#### 方案 A：临界区（关中断）
```c
__disable_irq();
counter++;
__enable_irq();
```
简单粗暴，但增加最坏中断延迟。

#### 方案 B：硬件原子指令
ARMv7-M 提供 LDREX/STREX 独占访问：
```c
uint32_t old, new;
do {
    old = __LDREXW(&counter);
    new = old + 1;
} while (__STREXW(new, &counter));
```
RISC-V 用 `lr.w / sc.w` 类似。这是 atomics、互斥锁、无锁队列的基石。

#### 方案 C：C11 `<stdatomic.h>`
```c
#include <stdatomic.h>
atomic_uint counter;
atomic_fetch_add(&counter, 1);
```
编译器选择 LDREX/STREX 或关中断实现，可移植。Cortex-M3+ 全支持。

第 11 章 [中断与异常](../11_中断与异常/) 会展开讨论。

---

## 3.8 内存屏障：CPU 的乱序与 `volatile` 不够用的时候

现代 CPU 会 **乱序执行** + **缓存写合并** + **读推测**。两条独立的内存操作的实际可见顺序可能和你代码里的顺序不同。

例：DMA 启动序列
```c
DMA_SRC = (uint32_t)buf;
DMA_DST = (uint32_t)UART_DR;
DMA_LEN = 100;
DMA_CTRL = ENABLE;     // ← 必须在前三个之后真的被外设看到
```

`volatile` 保证 **编译器不重排这四条**，但**不**保证 CPU / 总线不重排。需要 **内存屏障 (Memory Barrier)**：

| 指令      | ARM     | 含义                                  |
|-----------|---------|---------------------------------------|
| `DSB`     | Data Sync Barrier   | 等前面所有 mem 访问完成才继续     |
| `DMB`     | Data Mem Barrier    | 之前的 mem 访问对系统可见后才继续 |
| `ISB`     | Instr Sync Barrier  | 同步流水线，常用于改了系统寄存器后   |

C 写法：
```c
__DSB();           // CMSIS 提供的内建
```

什么时候需要：
- 启动 DMA 前
- 修改 NVIC / SCB 寄存器后
- 跨 CPU 共享数据更新后

第 13 章 DMA、第 27 章实时性深入会反复使用。

---

## 3.9 别名 (Aliasing) 与 strict-aliasing 规则

C99 起，编译器假设 **不同类型的指针不会指向同一对象**（除了 `char*` / `void*`）。这叫严格别名规则，是优化的基础。违反它行为未定义。

```c
uint32_t x = 0x1234;
float *fp = (float *)&x;
*fp = 1.0f;            // 严格别名违反 → 未定义
```

**正确做法**：

```c
/* 1. memcpy（最稳） */
float y;
memcpy(&y, &x, sizeof(y));

/* 2. union（GCC 友好但严格 C 标准灰色地带） */
union { uint32_t u; float f; } u = { .u = x };
float y = u.f;
```

外设映射时常用 `volatile uint32_t *` 强转，理论上属灰色地带，但实际所有嵌入式编译器都支持。可以理解为"打补丁的妥协"。

---

## 3.10 几条工程军规

1. **`size_t` 用于大小，`ptrdiff_t` 用于指针差**。别用 `int` 装内存大小。
2. **不要在头文件定义全局变量**，只声明（`extern`）。
3. **共享给 ISR 的变量必须 `volatile`**，最好同时考虑原子性。
4. **不要假定 enum 的底层类型大小**。需要时显式 `: uint8_t` 或用宏。
5. **MISRA-C 规则虽烦但救命**：第 44 章会详细讲，现在养成"不写花式 C"的习惯。

---

## 3.11 上手代码

`code/` 提供四个小程序，跑在你的开发机上（不需要 QEMU）：

- `mem_layout.c` —— 打印各种变量的地址，直观看见 `.text / .rodata / .data / .bss / stack / heap` 在内存哪里。
- `struct_pad.c` —— 演示 struct 的 padding 和 `packed` 差别。
- `volatile_demo.c` —— 编译 `-O0` vs `-O2` 看 `volatile` 和非 `volatile` 的汇编差异。
- `atomic_race.c` —— 用 pthread 在 PC 上重现 `counter++` 的丢失更新。

跑法：
```bash
cd code
make all
./mem_layout
./struct_pad
make show-volatile    # 输出 -O2 下两个版本的汇编对比
./atomic_race         # 看到丢失更新
```

---

## 3.12 自检题

1. 一个 `static const int N = 100;` 在文件作用域里定义，它住在哪里？
2. 下面哪些一定是原子的？  
   (a) `*(uint32_t *)0x2000_0000 = 0;`  
   (b) `*(uint64_t *)0x2000_0000 = 0;` （在 Cortex-M3 上）  
   (c) `g_counter++;`（`g_counter` 是 `uint32_t`）
3. 为什么 `volatile int *p` 和 `int * volatile p` 不一样？
4. 一个 `struct { uint8_t a; uint16_t b; uint8_t c; }` 在默认对齐下 `sizeof` 是多少？怎么调整字段顺序能更紧？
5. 启动 DMA 后没加 `__DSB()`，可能出什么问题？

答案见 `code/answers.md`。

---

## 3.13 与后续章节的联系

| 这章引出的概念       | 下游章节                                          |
|----------------------|---------------------------------------------------|
| 内存布局             | [09 启动文件与链接脚本](../09_启动文件与链接脚本/) |
| `volatile`           | [10 GPIO](../10_第一个程序_GPIO/) 起每章都用      |
| 原子性 / 临界区      | [11 中断](../11_中断与异常/)、[24 RTOS 概念](../24_RTOS概念与调度/) |
| 内存屏障             | [13 DMA](../13_DMA/)、[27 实时性](../27_实时性深入/) |
| struct 对齐 / packed | [15 UART](../15_UART/) 起协议章解析帧头          |

下一章 [04 电子电路最小集](../04_电子电路最小集/) 离开"软"，进入硬件世界。
