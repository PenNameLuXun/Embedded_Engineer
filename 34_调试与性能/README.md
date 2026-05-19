# 第 34 章　调试与性能：ftrace、perf、kgdb

> 嵌入式 Linux 工程师真正的工具不是 IDE，是 **ftrace、perf、bpftrace、kgdb** 这一套命令行工具。它们能告诉你 "上一秒 CPU 在干什么、那个驱动为什么变慢、谁触发了那个中断"。
>
> **学完本章你应该能**：(1) 用 ftrace 看每秒被 schedule 的所有进程，(2) 用 perf 找出系统瓶颈，(3) 知道 bpftrace 是 ftrace + perf 的"动态拼接器"，(4) 在 QEMU 上用 kgdb 调试内核。

---

## 34.1 工具地图

| 工具         | 干什么                          | 用例                            |
|--------------|---------------------------------|---------------------------------|
| **dmesg**    | 看内核日志                       | 启动失败、驱动 oops              |
| **ftrace**   | 内核函数级 trace                  | 调度延迟、中断耗时                |
| **perf**     | 性能采样 + 事件计数               | CPU 热点函数、Cache miss 率        |
| **bpftrace** | 动态注入脚本，灵活组合             | 一行命令统计 syscall 分布          |
| **strace**   | 跟用户进程的 syscall              | 进程卡哪、调谁                     |
| **ltrace**   | 跟用户进程的 libc 调用             | 找内存泄漏路径                     |
| **kgdb**     | 内核源码级 gdb 调试                | 改驱动 + 单步                     |
| **crash**    | 分析 kernel core dump              | 现场不能复现的崩溃                  |

---

## 34.2 ftrace：内核函数级跟踪

挂载点在 `/sys/kernel/tracing/`（旧路径 `/sys/kernel/debug/tracing/`）。

### 最简易用法：function tracer

```bash
echo function > /sys/kernel/tracing/current_tracer
echo 1 > /sys/kernel/tracing/tracing_on
sleep 1
echo 0 > /sys/kernel/tracing/tracing_on
cat /sys/kernel/tracing/trace | head
```

输出几千行内核函数调用记录。**用 `set_ftrace_filter` 限制范围**：

```bash
echo "i2c_*" > /sys/kernel/tracing/set_ftrace_filter
```

### function_graph tracer 看耗时

```bash
echo function_graph > current_tracer
echo i2c_transfer > set_graph_function
cat trace
```

输出形如：

```
2)               |  i2c_transfer() {
2)   1.234 us    |    i2c_check_for_quirks();
2) ! 423.000 us  |    __i2c_transfer();
2)               |  }
```

**带 `!` 标记的是耗时超过阈值的调用**。直接定位慢函数。

### tracepoint：内核埋点

ftrace 还能跟内核里预埋的"事件":

```bash
ls events/                    # sched / irq / block / net / ...
echo 1 > events/sched/sched_switch/enable
echo 1 > events/irq/irq_handler_entry/enable
cat trace_pipe                # 流式输出
```

看到每次进程切换、每次中断进入。**调度延迟问题这一招直接破案**。

---

## 34.3 perf：从用户态到内核的统一性能分析

### 找热点函数

```bash
perf record -g ./my_app           # 跑你的程序 + 采样
perf report                       # 交互式火焰图
```

样本统计每秒约 1000 次记录"当前 PC + 调用栈"。报告里前几名就是热点函数。

### 计数器

```bash
perf stat ./my_app
```

输出：

```
   245.32 ms task-clock                       
       142 context-switches                  
         5 cpu-migrations                   
       234 page-faults                       
  1234567890 cycles                          
  2345678901 instructions    # 1.90  insn per cycle
   123456789 branches        # 500 M/sec
     1234567 branch-misses   # 1.00% of all branches
       12345 cache-misses    
     2345678 cache-references                
```

`insn / cycle` < 1 说明 CPU 在等内存 (Cache miss、DRAM)；> 1 说明 SIMD / 多发射在工作。

### Flame Graph

社区工具 `flamegraph` 把 `perf record` 输出渲染成可视化火焰图，1 秒看清"程序 99% 时间花在哪条调用栈上"。

---

## 34.4 bpftrace：现代瑞士军刀

bpftrace 用类 awk 语法把"在哪里挂、采什么"用一行写出来：

```bash
# 1. 统计 read syscall 返回值分布
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @ = hist(args->ret); }'

# 2. 谁打开了 /etc/passwd
bpftrace -e 'tracepoint:syscalls:sys_enter_openat
             /str(args->filename) == "/etc/passwd"/
             { printf("%s\n", comm); }'

# 3. 量化 schedule 延迟（task ready → run 间隔）
bpftrace -e 'kprobe:wake_up_new_task { @s[args->p] = nsecs; }
             kprobe:finish_task_switch { @d = hist(nsecs - @s[arg0]); delete(@s[arg0]); }'
```

学习曲线大概 1 天。**学会后能解决 90% 性能 / 行为问题**。

---

## 34.5 kgdb：源码级单步内核

QEMU 上很方便：

```bash
# QEMU 启动加 -s
qemu-system-arm -M virt -kernel zImage ... -s -S -append "kgdbwait kgdboc=ttyAMA0,115200"

# 另一个终端
gdb-multiarch vmlinux
(gdb) target remote :1234
(gdb) b start_kernel
(gdb) c
```

进入 gdb 后能：
```
(gdb) bt
(gdb) p current
(gdb) p ((struct task_struct*)$x0)->comm
```

真硬件需要 USB-Serial + kgdboc 配置串口。

---

## 34.6 内核 panic / oops 分析

崩溃时 dmesg / 串口打印一段：

```
Unable to handle kernel paging request at virtual address ffffff80012345
...
PC is at my_driver_read+0x1c/0xa0 [my_driver]
LR is at ...
Stack: ... 0x1234 0x5678 ...
```

`addr2line -e my_driver.ko 0x1c` → 给出源码行。这是嵌入式 Linux 上调试 panic 的标准流程。

复杂场景用 `crash` 工具加载 `vmcore` (kdump 抓的内存镜像)，能像 gdb 一样浏览崩溃时的全部内核状态。

---

## 34.7 PREEMPT_RT：把 Linux 变实时

主线 Linux 不是硬实时（最大延迟到 ms 级）。**PREEMPT_RT 补丁**让几乎所有内核临界区可抢占 → 最大延迟降到 ~100 µs。

```bash
# Buildroot 选 BR2_LINUX_KERNEL_EXT_PREEMPT_RT_PATCH
# 内核 config 选 CONFIG_PREEMPT_RT_FULL=y
```

cyclictest 工具量延迟：

```
cyclictest -p 99 -t 1 -n
# 输出 max latency 在 µs 级
```

工业 / 机器人 / 音视频实时性要求用这套。**RTOS 替代品就是它**。

---

## 34.8 实用速查命令

```bash
# 内核态
dmesg -w                          # 实时日志
/proc/interrupts                  # IRQ 分布
/proc/sys/kernel/sched_*          # 调度参数
/sys/kernel/tracing/...           # ftrace
/sys/kernel/debug/...             # debugfs

# 用户态
top / htop                        # 进程概览
iotop                              # IO 占用
iftop                              # 网络占用
strace -f -p PID                   # 跟某进程
ltrace -p PID                      # libc 调用
gdb -p PID                         # 接进去看

# 找谁占了内核内存
slabtop
cat /proc/meminfo
```

---

## 34.9 自检题

1. 一个驱动加载后系统变慢，先看哪几个工具？
2. ftrace 和 perf 都能找慢，差别？
3. PREEMPT_RT 不能完全替代 RTOS 的根本原因？
4. eBPF / bpftrace 相对传统 ftrace 的"杀手"特性？

答案见 `code/answers.md`。

---

## 34.10 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| WCET 测量          | [27 实时性深入](../27_实时性深入/) 回顾    |
| OTA 后回归测试     | [42 OTA](../42_OTA_固件升级/)              |
| 安全审计 + ftrace | [40 嵌入式安全](../40_嵌入式安全/)         |
| ARM Tracing (ETM) | [38 SoC 集成](../38_集成软核SoC/)          |

---

## Part 5 收尾

Part 5 嵌入式 Linux 7 章完成：

| 章 | 主题            | 关键收获                         |
|----|-----------------|----------------------------------|
| 28 | 启动流程         | BootROM → SPL → U-Boot → Kernel → init |
| 29 | 交叉编译+Buildroot | 5 分钟 build 完整镜像               |
| 30 | 设备树           | DTS 语法、compatible、overlay     |
| 31 | 字符设备驱动     | module + cdev + fops + copy_*    |
| 32 | 子系统驱动模型   | platform / I²C / SPI / GPIO       |
| 33 | 用户态接口       | sysfs / netlink / UIO / ioctl     |
| 34 | 调试与性能       | ftrace / perf / bpftrace / kgdb   |

下一部分 [Part 6 SoC / FPGA](../35_Verilog入门/) 完全离开软件视角，回到硬件描述语言。
