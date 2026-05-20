#!/usr/bin/env python3
"""教材配图生成脚本

一次性生成全部 45 章的关键图，保存到各章 images/ 子目录。

依赖：
    pip3 install matplotlib pillow
    系统：fonts-noto-cjk

跑法：
    python3 scripts/gen_diagrams.py            # 全部生成
    python3 scripts/gen_diagrams.py ch02 ch18  # 只生成指定章节

风格：白底 + 色块 + 圆角 + 中文标签。
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle, PathPatch
from matplotlib.path import Path as MplPath

mpl.rcParams['font.family'] = 'Noto Sans CJK JP'
mpl.rcParams['axes.unicode_minus'] = False

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


# ============================================================
# 公共工具
# ============================================================
def new_fig(w=10, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    return fig, ax

def save(fig, chapter_dir, name):
    out_dir = os.path.join(BASE, chapter_dir, "images")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  -> {chapter_dir}/images/{name}")

def box(ax, x, y, w, h, text, color="#3498db", text_color="white",
        fontsize=10, bold=True, rounding=0.04):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        linewidth=1.2, edgecolor='black', facecolor=color, alpha=0.85,
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, color=text_color,
            fontweight='bold' if bold else 'normal')

def arrow(ax, x1, y1, x2, y2, color='#333', lw=1.5, style='->'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))

def setup(ax, xlim, ylim, title=None):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis('off')
    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)


# ============================================================
# Ch 00 导论 —— 硬件层次
# ============================================================
def ch00():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 7), "嵌入式硬件层次（第 00 章）")
    levels = [
        ("板级 Board (PCB / 电源 / 传感器 / 执行器)", 0.5, 0.5, 10, 1.0, "#34495e"),
        ("芯片 / SoC (一颗硅片)",                  1.5, 1.8, 8,  1.0, "#3498db"),
        ("IP 核 (CPU / UART / DMA / PHY ...)",      2.5, 3.1, 6,  1.0, "#2ecc71"),
        ("门 / 触发器 / 寄存器",                    3.5, 4.4, 4,  1.0, "#f39c12"),
        ("晶体管",                                  4.5, 5.7, 2,  0.8, "#e74c3c"),
    ]
    for label, x, y, w, h, c in levels:
        box(ax, x, y, w, h, label, color=c, fontsize=11)
    ax.text(0.3, 0.0, "越往下越微观", fontsize=9, color="#666", style='italic')
    save(fig, "00_导论", "hardware_layers.png")


# ============================================================
# Ch 01 数字与逻辑 —— D 触发器 setup/hold
# ============================================================
def ch01():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "D 触发器与 setup/hold 时间（第 01 章）")
    # D signal
    ax.plot([0, 2.5], [4, 4], 'k-', lw=2)
    ax.plot([2.5, 3.2], [4, 3], 'k-', lw=2)  # transition
    ax.plot([3.2, 7, 7.7], [3, 3, 4], 'k-', lw=2)
    ax.plot([7.7, 10], [4, 4], 'k-', lw=2)
    ax.text(0.2, 4.5, "D", fontsize=12, fontweight='bold')

    # CLK
    clk_y = 1.5
    pts_x = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10]
    pts_y = [clk_y, clk_y, clk_y+0.8, clk_y+0.8, clk_y, clk_y,
             clk_y+0.8, clk_y+0.8, clk_y, clk_y, clk_y+0.8, clk_y+0.8,
             clk_y, clk_y, clk_y+0.8, clk_y+0.8, clk_y, clk_y, clk_y+0.8, clk_y+0.8]
    ax.plot(pts_x, pts_y, 'b-', lw=2)
    ax.text(0.2, clk_y+0.4, "CLK", fontsize=12, fontweight='bold', color='blue')

    # mark setup/hold around rising edge at x=5
    edge_x = 5
    ax.axvline(edge_x, color='red', linestyle=':', alpha=0.5)
    ax.fill_between([edge_x-0.6, edge_x], 0, 5, color='#e74c3c', alpha=0.15)
    ax.fill_between([edge_x, edge_x+0.4], 0, 5, color='#27ae60', alpha=0.15)
    ax.text(edge_x-0.3, 4.7, "t_setup", ha='center', color='#c0392b', fontsize=10)
    ax.text(edge_x+0.2, 4.7, "t_hold", ha='center', color='#27ae60', fontsize=10)
    ax.annotate('上升沿采样', xy=(edge_x, clk_y+0.8), xytext=(edge_x+1.5, clk_y+1.5),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    save(fig, "01_数字与逻辑基础", "dff_timing.png")


# ============================================================
# Ch 02 体系结构 —— 内存层级 (已有，但重做以保持一致)
# ============================================================
def ch02():
    fig, ax = new_fig(10, 7)
    setup(ax, (0, 10), (0, 10), "内存层级 (第 02 章)")
    levels = [
        ("寄存器",     "~0.3 ns",  "几十字节",      9.0, 2.0, "#e74c3c"),
        ("L1 Cache",   "~1 ns",    "几十 KB",       8.0, 3.0, "#e67e22"),
        ("L2 Cache",   "~3 ns",    "几百 KB",       7.0, 4.0, "#f39c12"),
        ("L3 Cache",   "~10 ns",   "MB 级",         6.0, 5.0, "#f1c40f"),
        ("DRAM",       "~80 ns",   "几百 MB - GB",  5.0, 6.0, "#2ecc71"),
        ("NOR Flash",  "50-100 ns","MB 级",         4.0, 7.0, "#16a085"),
        ("NAND / SSD", "25 µs - ms","GB 级",        3.0, 8.0, "#3498db"),
        ("网络 / 远端","> 1 ms",    "巨大",          2.0, 9.0, "#9b59b6"),
    ]
    cx = 5.0; bh = 0.7
    for label, lat, sz, y, w, c in levels:
        box(ax, cx - w/2, y - bh/2, w, bh, label, color=c, fontsize=11)
        ax.text(cx + w/2 + 0.2, y, lat, ha='left', va='center', fontsize=9, color='#333')
        ax.text(cx - w/2 - 0.2, y, sz, ha='right', va='center', fontsize=9, color='#666')
    save(fig, "02_计算机体系结构速通", "memory_hierarchy.png")


# ============================================================
# Ch 03 C 再训练 —— 内存布局
# ============================================================
def ch03():
    fig, ax = new_fig(8, 9)
    setup(ax, (0, 8), (0, 11), "嵌入式 C 程序内存布局（第 03 章）")
    sections = [
        ("外设寄存器 (Peripheral)", 10, "#9b59b6", "0xFFFF_FFFF"),
        ("Stack ↓ (向下增长)",      8.5, "#3498db", ""),
        ("Heap ↑ (可选)",            7, "#1abc9c", ""),
        (".bss (未初始化全局)",      5.8, "#2ecc71", ""),
        (".data (已初始化全局)",     5.0, "#27ae60", "RAM"),
        (".rodata (常量 / 字符串)",  3.5, "#f39c12", ""),
        (".text (代码)",            2.5, "#e67e22", "Flash"),
        ("中断向量表",               1.5, "#e74c3c", "0x0000_0000"),
    ]
    x = 1.5; w = 5.0
    for label, y, c, ann in sections:
        box(ax, x, y, w, 1.0, label, color=c, fontsize=10)
        if ann:
            ax.text(x + w + 0.2, y + 0.5, ann, fontsize=9, color='#555')
    # divider line between RAM and Flash
    ax.plot([x, x+w], [4.5, 4.5], 'k--', lw=1.5, alpha=0.6)
    ax.text(x + w + 1.5, 7, "RAM", fontsize=12, fontweight='bold', color='#27ae60')
    ax.text(x + w + 1.5, 2.5, "Flash", fontsize=12, fontweight='bold', color='#e67e22')
    save(fig, "03_C语言再训练", "memory_layout.png")


# ============================================================
# Ch 04 电路 —— 推挽 vs 开漏
# ============================================================
def ch04():
    fig, axs = plt.subplots(1, 2, figsize=(11, 5))
    for ax in axs: ax.axis('off'); ax.set_xlim(0, 5); ax.set_ylim(0, 6)

    # Push-Pull
    ax = axs[0]
    ax.set_title("推挽 (Push-Pull)", fontsize=12, fontweight='bold')
    ax.plot([2.5, 2.5], [5, 5.5], 'k-', lw=2)
    ax.text(2.5, 5.7, "VCC", ha='center', fontsize=10)
    box(ax, 2.0, 4.0, 1.0, 0.8, "PMOS", color="#3498db", fontsize=10)
    box(ax, 2.0, 2.5, 1.0, 0.8, "NMOS", color="#e74c3c", fontsize=10)
    ax.plot([2.5, 2.5], [3.3, 4.0], 'k-', lw=2)
    ax.plot([2.5, 4.0], [3.65, 3.65], 'k-', lw=2)
    ax.text(4.1, 3.65, "pin", fontsize=11, va='center', fontweight='bold')
    ax.plot([2.5, 2.5], [1.5, 2.5], 'k-', lw=2)
    ax.text(2.5, 1.3, "GND", ha='center', fontsize=10)
    ax.text(2.5, 0.5, "能强力驱动 0 和 1", ha='center', fontsize=10, style='italic', color='#666')

    # Open-Drain
    ax = axs[1]
    ax.set_title("开漏 (Open-Drain) + 外部上拉", fontsize=12, fontweight='bold')
    ax.plot([2.5, 2.5], [5, 5.5], 'k-', lw=2)
    ax.text(2.5, 5.7, "VCC", ha='center', fontsize=10)
    box(ax, 2.2, 4.2, 0.6, 0.6, "R_p", color="#f39c12", fontsize=9)
    ax.plot([2.5, 2.5], [3.65, 4.2], 'k-', lw=2)
    ax.plot([2.5, 4.0], [3.65, 3.65], 'k-', lw=2)
    ax.text(4.1, 3.65, "pin", fontsize=11, va='center', fontweight='bold')
    box(ax, 2.0, 2.5, 1.0, 0.8, "NMOS", color="#e74c3c", fontsize=10)
    ax.plot([2.5, 2.5], [3.3, 3.65], 'k-', lw=2)
    ax.plot([2.5, 2.5], [1.5, 2.5], 'k-', lw=2)
    ax.text(2.5, 1.3, "GND", ha='center', fontsize=10)
    ax.text(2.5, 0.5, "释放 = 高阻；多路并联 = wired-AND", ha='center', fontsize=9.5,
            style='italic', color='#666')

    plt.suptitle("GPIO 驱动方式对比（第 04 章）", fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, "04_电子电路最小集", "push_pull_vs_open_drain.png")


# ============================================================
# Ch 05 数字时序 —— 两级 FF 同步器
# ============================================================
def ch05():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "跨时钟域两级 FF 同步器（第 05 章）")
    # Source domain
    ax.text(1.5, 4.3, "时钟域 A", fontsize=11, fontweight='bold', color='#3498db')
    box(ax, 0.5, 2.5, 2, 1.2, "源信号\n(async)", color="#3498db", fontsize=10)
    # FF1
    box(ax, 4.0, 2.5, 1.5, 1.2, "FF1", color="#e74c3c", fontsize=11)
    # FF2
    box(ax, 6.5, 2.5, 1.5, 1.2, "FF2", color="#e74c3c", fontsize=11)
    # Use
    box(ax, 9.0, 2.5, 1.7, 1.2, "B 域\n用户逻辑", color="#27ae60", fontsize=10)
    # Arrows
    arrow(ax, 2.5, 3.1, 4.0, 3.1)
    arrow(ax, 5.5, 3.1, 6.5, 3.1)
    arrow(ax, 8.0, 3.1, 9.0, 3.1)
    # Clk_b shared
    ax.text(8, 1.5, "clk_b", fontsize=10, color='#e74c3c', fontweight='bold')
    arrow(ax, 4.75, 1.7, 4.75, 2.5, color='#e74c3c')
    arrow(ax, 7.25, 1.7, 7.25, 2.5, color='#e74c3c')
    ax.plot([4.75, 7.25], [1.7, 1.7], 'r-', lw=1)
    # Annotations
    ax.text(4.75, 4.1, "可能亚稳", fontsize=9, color='#c0392b', ha='center', style='italic')
    ax.text(7.25, 4.1, "稳定", fontsize=9, color='#27ae60', ha='center', style='italic')
    save(fig, "05_数字电路与时序", "two_flop_synchronizer.png")


# ============================================================
# Ch 06 总线时序图 —— VALID/READY 握手
# ============================================================
def ch06():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "VALID/READY 握手（AXI 风格，第 06 章）")
    # CLK
    y = 4
    pts = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10]
    ys = [y, y, y+0.5, y+0.5, y, y, y+0.5, y+0.5, y, y, y+0.5, y+0.5,
          y, y, y+0.5, y+0.5, y, y, y+0.5, y+0.5]
    ax.plot(pts, ys, 'b-', lw=1.5)
    ax.text(-0.3, 4.2, "CLK", fontsize=10, ha='right', fontweight='bold')

    # VALID
    y = 3
    ax.plot([0, 3, 3, 6, 6, 10], [y, y, y+0.5, y+0.5, y, y], 'k-', lw=1.5)
    ax.text(-0.3, 3.2, "VALID", fontsize=10, ha='right', fontweight='bold')

    # READY
    y = 2
    ax.plot([0, 5, 5, 7, 7, 10], [y, y, y+0.5, y+0.5, y, y], 'k-', lw=1.5)
    ax.text(-0.3, 2.2, "READY", fontsize=10, ha='right', fontweight='bold')

    # DATA
    y = 1
    ax.fill_between([3, 6], y, y+0.5, color="#bdc3c7", alpha=0.5)
    ax.text(4.5, 1.25, "DATA", ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(-0.3, 1.2, "DATA", fontsize=10, ha='right', fontweight='bold')

    # Mark handshake
    ax.axvline(5, color='red', linestyle=':', alpha=0.6)
    ax.axvline(6, color='red', linestyle=':', alpha=0.6)
    ax.text(5.5, 0.3, "VALID && READY\n本拍传输", ha='center', color='red', fontsize=10)
    save(fig, "06_总线与时序图", "valid_ready_handshake.png")


# ============================================================
# Ch 07 QEMU 工具链 —— 流程图
# ============================================================
def ch07():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "QEMU 工具链工作流（第 07 章）")
    steps = [
        (0.5, "C 源码\n*.c, *.s, *.ld", "#3498db"),
        (3.0, "arm-none-eabi-gcc\n交叉编译", "#e67e22"),
        (5.5, "ELF 镜像\nhello.elf", "#2ecc71"),
        (8.0, "qemu-system-arm\n模拟 lm3s6965evb", "#9b59b6"),
    ]
    for x, label, c in steps:
        box(ax, x, 2, 2.0, 1.5, label, color=c, fontsize=10)
    for i in range(3):
        arrow(ax, 0.5 + 2.0 + 2.5*i, 2.75, 3.0 + 2.5*i, 2.75)
    # GDB
    box(ax, 8.0, 0.2, 2.0, 1.0, "gdb-multiarch\n远程调试", color="#e74c3c", fontsize=10)
    arrow(ax, 9.0, 1.95, 9.0, 1.25, color='#e74c3c')
    save(fig, "07_QEMU与工具链搭建", "toolchain_flow.png")


# ============================================================
# Ch 08 Cortex-M —— 内存映射
# ============================================================
def ch08():
    fig, ax = new_fig(8, 9)
    setup(ax, (0, 8), (0, 11), "ARMv7-M 标准内存映射（第 08 章）")
    regions = [
        ("Code Region\n(Flash 映射)",         0.5, "#e67e22", "0x0000_0000"),
        ("SRAM Region\n(片上 SRAM)",           2.0, "#2ecc71", "0x2000_0000"),
        ("Peripheral Region\n(各类外设)",       3.5, "#3498db", "0x4000_0000"),
        ("External RAM\n(片外 RAM)",           5.0, "#1abc9c", "0x6000_0000"),
        ("External Device",                    6.5, "#95a5a6", "0xA000_0000"),
        ("PPB (内核私有外设)\nNVIC/SysTick/MPU",8.0, "#9b59b6", "0xE000_0000"),
    ]
    for label, y, c, addr in regions:
        box(ax, 1.5, y, 4.5, 1.2, label, color=c, fontsize=10)
        ax.text(0.5, y + 0.6, addr, fontsize=9, color='#333', family='monospace', va='center')
    ax.text(6.5, 9.5, "0xFFFF_FFFF", fontsize=9, color='#333', family='monospace')
    save(fig, "08_ARM_Cortex_M_架构", "memory_map.png")


# ============================================================
# Ch 09 启动 + 链接 —— VMA vs LMA
# ============================================================
def ch09():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 6), ".data 的 LMA → VMA 启动时拷贝（第 09 章）")
    # Flash side
    ax.text(2, 5.3, "Flash (LMA)", fontsize=12, fontweight='bold', color='#e67e22')
    box(ax, 1, 3.5, 2.5, 1.0, ".text + .rodata", color="#e67e22", fontsize=10)
    box(ax, 1, 2.0, 2.5, 1.0, ".data 初值", color="#f39c12", fontsize=10)
    # SRAM side
    ax.text(8.5, 5.3, "SRAM (VMA)", fontsize=12, fontweight='bold', color='#2ecc71')
    box(ax, 7.5, 3.5, 2.5, 1.0, ".data 工作区", color="#2ecc71", fontsize=10)
    box(ax, 7.5, 2.0, 2.5, 1.0, ".bss (清零)", color="#27ae60", fontsize=10)
    box(ax, 7.5, 0.5, 2.5, 1.0, "Stack / Heap", color="#3498db", fontsize=10)
    # Arrow Flash .data initials -> SRAM .data
    arrow(ax, 3.5, 2.5, 7.5, 4.0, color='#e74c3c', lw=2)
    ax.text(5.5, 3.7, "Reset_Handler 拷贝", color='#c0392b', fontsize=10, fontweight='bold')
    # bss clear
    arrow(ax, 5.5, 0.8, 7.5, 2.4, color='#27ae60', lw=2)
    ax.text(5.5, 1.3, "清零", color='#27ae60', fontsize=10, fontweight='bold')
    save(fig, "09_启动文件与链接脚本", "vma_lma.png")


# ============================================================
# Ch 10 GPIO/UART —— 初始化序列
# ============================================================
def ch10():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 6), "UART 初始化标准六步（第 10 章）")
    steps = [
        "① 开外设时钟\nRCGC1.UART0=1",
        "② 配置 GPIO 复用\nAFSEL + DEN",
        "③ 关 UART\n清 UARTEN",
        "④ 设波特率\nIBRD + FBRD",
        "⑤ 设帧格式\nLCRH = 8N1",
        "⑥ 使能 UART\nUARTEN + TXE + RXE",
    ]
    colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6", "#1abc9c"]
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.3 + (i % 3) * 3.7
        y = 3.5 - (i // 3) * 2.5
        box(ax, x, y, 3.2, 1.7, s, color=c, fontsize=10)
    save(fig, "10_第一个程序_GPIO", "uart_init_steps.png")


# ============================================================
# Ch 11 中断 —— ISR 进入流程
# ============================================================
def ch11():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 6), "Cortex-M 中断进入流程（第 11 章）")
    steps = [
        (0.3, "1. 当前指令\n执行完", "#3498db"),
        (2.5, "2. 硬件 stacking\nR0-R3,R12,LR,PC,xPSR", "#9b59b6"),
        (5.0, "3. LR ← 0xFFFF_FFFx\n(EXC_RETURN)", "#e67e22"),
        (7.3, "4. PC ← 向量表[n]", "#f39c12"),
        (9.5, "5. 进 Handler 模式\n开跑 ISR", "#e74c3c"),
    ]
    for x, s, c in steps:
        box(ax, x, 3, 1.9, 1.5, s, color=c, fontsize=9.5)
    for i in range(4):
        arrow(ax, 0.3 + 1.9 + 2.2*i, 3.75, 2.5 + 2.2*i, 3.75)
    # ISR exit notes
    ax.text(5.5, 1.5,
            "退出时硬件反向 unstacking：\nLR=EXC_RETURN 触发自动 pop → 原任务恢复",
            ha='center', fontsize=10, color='#27ae60',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#e8f5e9', edgecolor='#27ae60'))
    save(fig, "11_中断与异常", "isr_entry_flow.png")


# ============================================================
# Ch 12 定时器 —— SysTick 节拍
# ============================================================
def ch12():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "SysTick 周期性中断（第 12 章）")
    # Tick markers
    for i, x in enumerate([1, 2.5, 4, 5.5, 7, 8.5, 10]):
        ax.axvline(x, color='#3498db', linestyle='-', alpha=0.6, lw=1.5)
        ax.text(x, 4.5, f"tick {i}", ha='center', fontsize=9, color='#2980b9')
    # Time axis
    ax.annotate('', xy=(10.5, 1.5), xytext=(0.5, 1.5),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(10.7, 1.5, "时间", fontsize=10, va='center')
    # SysTick ISR markers
    for x in [1, 2.5, 4, 5.5, 7, 8.5, 10]:
        box(ax, x - 0.3, 2.5, 0.6, 0.8, "ISR", color="#e74c3c", fontsize=9)
    ax.text(5.5, 0.5, "SYST_LOAD = (CPU_HZ / 1000) - 1   →   每 1 ms 触发 SysTick_Handler",
            ha='center', fontsize=10, color='#333', style='italic')
    save(fig, "12_定时器与SysTick", "systick_periodic.png")


# ============================================================
# Ch 13 DMA —— ping-pong 双缓冲
# ============================================================
def ch13():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 6), "DMA Ping-Pong 双缓冲（第 13 章）")
    box(ax, 0.5, 4, 1.8, 1.5, "外设\n(ADC/UART)", color="#3498db", fontsize=10)
    box(ax, 3.5, 4, 1.8, 1.5, "DMA 引擎", color="#9b59b6", fontsize=10)
    box(ax, 6.5, 4.6, 2.0, 1.0, "Buffer A\n(正在写)", color="#e74c3c", fontsize=10)
    box(ax, 6.5, 3.0, 2.0, 1.0, "Buffer B\n(空闲)", color="#95a5a6", fontsize=10)
    box(ax, 9.5, 3.6, 1.4, 1.4, "CPU\n(处理)", color="#2ecc71", fontsize=10)
    arrow(ax, 2.3, 4.7, 3.5, 4.7)
    arrow(ax, 5.3, 5.0, 6.5, 5.0, color='#e74c3c', lw=2)
    arrow(ax, 8.5, 5.0, 9.5, 4.5, color='#27ae60', lw=2)
    ax.text(5.5, 1.5,
            "A 写满 → DMA 切到 B，CPU 处理 A；B 写满 → 切回 A，CPU 处理 B\nCPU 与 DMA 永不冲突",
            ha='center', fontsize=10.5, color='#333',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#fff3e0', edgecolor='#e67e22'))
    save(fig, "13_DMA", "ping_pong.png")


# ============================================================
# Ch 14 ADC —— 采样定理示意
# ============================================================
def ch14():
    import numpy as np
    fig, axs = plt.subplots(2, 1, figsize=(11, 6))
    t = np.linspace(0, 1, 1000)
    sig = np.sin(2 * np.pi * 3 * t)

    ax = axs[0]
    ax.plot(t, sig, 'b-', lw=1, alpha=0.4, label='原信号')
    ts = np.linspace(0, 1, 31)
    ax.stem(ts, np.sin(2 * np.pi * 3 * ts), basefmt=" ", linefmt='g-', markerfmt='go')
    ax.set_title("采样率充足 (>2× 信号频率)：能重建", fontsize=11, fontweight='bold')
    ax.set_ylabel("幅值"); ax.legend(loc='upper right'); ax.grid(alpha=0.3)

    ax = axs[1]
    ax.plot(t, sig, 'b-', lw=1, alpha=0.4, label='原信号 3 Hz')
    ts2 = np.linspace(0, 1, 5)
    aliased_y = np.sin(2 * np.pi * 3 * ts2)
    ax.stem(ts2, aliased_y, basefmt=" ", linefmt='r-', markerfmt='ro')
    t2 = np.linspace(0, 1, 1000)
    ax.plot(t2, np.sin(2 * np.pi * 1 * t2), 'r--', lw=1, alpha=0.6, label='看起来像 1 Hz（混叠）')
    ax.set_title("采样率不足：混叠 (aliasing)", fontsize=11, fontweight='bold')
    ax.set_xlabel("时间"); ax.set_ylabel("幅值"); ax.legend(loc='upper right'); ax.grid(alpha=0.3)

    plt.suptitle("Nyquist 采样定理（第 14 章）", fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "14_ADC_DAC", "nyquist.png")


# ============================================================
# Ch 15 UART —— 帧结构
# ============================================================
def ch15():
    fig, ax = new_fig(12, 4)
    setup(ax, (0, 12), (0, 5), "UART 8N1 帧结构（第 15 章）")
    # idle high
    ax.plot([0, 1], [3, 3], 'b-', lw=2)
    ax.plot([1, 1], [3, 1.5], 'b-', lw=2)
    ax.plot([1, 2], [1.5, 1.5], 'b-', lw=2)  # start bit low
    # 8 data bits (alternating example)
    bits = [1, 0, 1, 1, 0, 1, 0, 1]  # arbitrary
    x = 2
    for i, b in enumerate(bits):
        y = 3 if b else 1.5
        ax.plot([x, x+0.8], [y, y], 'b-', lw=2)
        # transition
        next_y = 3 if (i + 1 < len(bits) and bits[i + 1]) else 1.5
        ax.plot([x+0.8, x+0.8], [y, next_y], 'b-', lw=0.5, alpha=0.3)
        ax.text(x+0.4, y - 0.3 if b else y - 0.3, f"D{i}", ha='center', fontsize=8, color='#333')
        x += 0.8
    # stop bit (high)
    ax.plot([x, x], [1.5, 3], 'b-', lw=2)
    ax.plot([x, x+1], [3, 3], 'b-', lw=2)
    # labels
    ax.text(0.5, 3.4, "Idle", fontsize=10, color='#666')
    ax.text(1.5, 0.8, "Start (0)", ha='center', fontsize=10, color='#e74c3c', fontweight='bold')
    ax.text(5.5, 0.5, "8 data bits (LSB first)", ha='center', fontsize=10, color='#2ecc71', fontweight='bold')
    ax.text(x + 0.5, 3.4, "Stop (1)", ha='center', fontsize=10, color='#27ae60', fontweight='bold')
    save(fig, "15_UART", "uart_frame.png")


# ============================================================
# Ch 16 SPI —— 4 模式 (CPOL/CPHA)
# ============================================================
def ch16():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "SPI 四种模式 (CPOL/CPHA, 第 16 章)")
    modes = [
        ("Mode 0\nCPOL=0 CPHA=0", 0, 5, "#3498db"),
        ("Mode 1\nCPOL=0 CPHA=1", 6, 5, "#9b59b6"),
        ("Mode 2\nCPOL=1 CPHA=0", 0, 1.5, "#e67e22"),
        ("Mode 3\nCPOL=1 CPHA=1", 6, 1.5, "#e74c3c"),
    ]
    # tiny clock waveforms
    import numpy as np
    for label, xs, ys, c in modes:
        ax.text(xs + 0.3, ys + 1.6, label, fontsize=10, fontweight='bold', color=c)
        # draw SCK
        cpol = 1 if "CPOL=1" in label else 0
        sck_low = ys + 0.5
        sck_high = ys + 1.1
        if cpol == 0:
            y_base = sck_low; y_top = sck_high
        else:
            y_base = sck_high; y_top = sck_low
        seg_x = [xs+0.3]
        seg_y = [y_base]
        for i in range(4):
            seg_x += [xs+0.3 + 1.0*i + 0.5, xs+0.3 + 1.0*i + 0.5, xs+0.3 + 1.0*i + 1.0, xs+0.3 + 1.0*i + 1.0]
            seg_y += [y_base, y_top, y_top, y_base]
        ax.plot(seg_x, seg_y, color=c, lw=2)
        ax.text(xs + 0.05, (sck_low + sck_high)/2, "SCK", fontsize=9, ha='right', va='center')
    save(fig, "16_SPI", "spi_modes.png")


# ============================================================
# Ch 17 I2C —— 仲裁示意
# ============================================================
def ch17():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 6), "I²C 多主仲裁（第 17 章）")
    # Master A: 0x42 = 0100 0010
    ax.text(0.3, 4.5, "主 A (0x42 = 0100_0010)", fontsize=10, fontweight='bold', color='#3498db')
    bits_a = [0, 1, 0, 0, 0, 0, 1, 0]
    bits_b = [0, 1, 0, 0, 0, 0, 0, 0]  # 0x40
    bits_l = [0, 1, 0, 0, 0, 0, 0, 0]  # observed = AND

    def draw_bits(y, bits, color, label):
        ax.text(0.3, y + 0.5, label, fontsize=10, fontweight='bold', color=color)
        for i, b in enumerate(bits):
            x = 2.5 + i * 0.9
            color_b = color if b == 1 else '#bdc3c7'
            ax.plot([x, x + 0.7], [y + (0.6 if b else 0.1), y + (0.6 if b else 0.1)], color=color, lw=3)
            ax.text(x + 0.35, y - 0.15, str(b), ha='center', fontsize=9)
    draw_bits(4.0, bits_a, '#3498db', "主 A")
    draw_bits(2.8, bits_b, '#e74c3c', "主 B (0x40)")
    draw_bits(1.5, bits_l, '#9b59b6', "线 (wired-AND)")
    # Mark losing bit
    ax.axvline(2.5 + 6 * 0.9 + 0.35, color='#e74c3c', linestyle=':', lw=2)
    ax.text(2.5 + 6 * 0.9 + 0.35, 5.4,
            "第 6 位：A 想发 1，B 发 0\n线上 = 0 → A 输",
            ha='center', fontsize=9, color='#c0392b')
    save(fig, "17_I2C_SMBus", "arbitration.png")


# ============================================================
# Ch 18 CAN —— 帧结构 (已有，重做)
# ============================================================
def ch18():
    fig, ax = new_fig(14, 4)
    setup(ax, (0, 100), (0, 10), "CAN 2.0A 标准帧布局（第 18 章）")
    fields = [
        ("SOF\n1 bit", 3, "#e74c3c"),
        ("ID (11 bits)", 15, "#3498db"),
        ("RTR\n1 bit", 3, "#e67e22"),
        ("IDE+r0\n2 bits", 4, "#95a5a6"),
        ("DLC\n4 bits", 5, "#95a5a6"),
        ("Data (0-64 bits)", 25, "#2ecc71"),
        ("CRC (15 bits)\n+ 定界符", 15, "#9b59b6"),
        ("ACK\n2 bits", 5, "#1abc9c"),
        ("EOF\n7 bits", 8, "#34495e"),
        ("IFS\n3 bits", 5, "#7f8c8d"),
    ]
    y_low, y_high = 4.5, 7.5
    x = 5
    for label, w, c in fields:
        rect = Rectangle((x, y_low), w, y_high - y_low,
                         linewidth=1.2, edgecolor='black',
                         facecolor=c, alpha=0.85)
        ax.add_patch(rect)
        ax.text(x + w/2, (y_low + y_high)/2, label, ha='center', va='center',
                fontsize=9.5, color='white', fontweight='bold')
        x += w
    arb_start = 5 + 3; arb_end = 5 + 3 + 15 + 3
    ax.annotate('', xy=(arb_end, 8.0), xytext=(arb_start, 8.0),
                arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=2))
    ax.text((arb_start + arb_end)/2, 8.4, "仲裁段（决定优先级）",
            ha='center', va='bottom', fontsize=10, color='#e74c3c', fontweight='bold')
    ax.text(50, 2.5,
            "线与机制：dominant '0' 覆盖 recessive '1'。ID 越小优先级越高。",
            ha='center', va='center', fontsize=9.5, color='#555', style='italic')
    save(fig, "18_CAN_CANFD", "can_frame_layout.png")


# ============================================================
# Ch 19 USB —— 枚举流程
# ============================================================
def ch19():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 8), "USB 设备枚举流程（第 19 章）")
    steps = [
        "1. 物理插入\nD+/D- 上拉变化",
        "2. Host 复位设备",
        "3. GET_DESCRIPTOR(DEVICE)\n收 18 字节",
        "4. SET_ADDRESS(addr)\n设备改用新地址",
        "5. GET_DESCRIPTOR(CONFIG)\n+ 接口 + 端点",
        "6. SET_CONFIGURATION(1)\n设备就绪",
        "7. Host 加载 class driver\n→ 设备可用",
    ]
    for i, s in enumerate(steps):
        x = 0.3 + (i % 4) * 2.7
        y = 6 - (i // 4) * 2.5
        c = ["#3498db", "#9b59b6", "#e67e22", "#f39c12", "#2ecc71", "#1abc9c", "#e74c3c"][i]
        box(ax, x, y, 2.4, 1.7, s, color=c, fontsize=9.5)
        if i < 6:
            if (i + 1) % 4 == 0:
                # newline arrow
                pass
            else:
                arrow(ax, x + 2.4, y + 0.85, x + 2.7, y + 0.85)
    save(fig, "19_USB概览", "enumeration.png")


# ============================================================
# Ch 20 Ethernet —— TCP 三次握手
# ============================================================
def ch20():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "TCP 三次握手（第 20 章）")
    box(ax, 1, 5.5, 2, 1, "Client", color="#3498db", fontsize=11)
    box(ax, 8, 5.5, 2, 1, "Server", color="#e74c3c", fontsize=11)
    # arrows
    arrow(ax, 3, 5.2, 8, 4.5)
    ax.text(5.5, 5.0, "SYN  seq=X", fontsize=11, color='#3498db', fontweight='bold', ha='center')
    arrow(ax, 8, 4.0, 3, 3.3)
    ax.text(5.5, 3.8, "SYN+ACK  seq=Y, ack=X+1", fontsize=11, color='#e74c3c', fontweight='bold', ha='center')
    arrow(ax, 3, 2.8, 8, 2.1)
    ax.text(5.5, 2.6, "ACK  ack=Y+1", fontsize=11, color='#3498db', fontweight='bold', ha='center')
    box(ax, 4, 0.3, 3, 1, "双方 ESTABLISHED", color="#27ae60", fontsize=11)
    save(fig, "20_Ethernet_TCPIP", "tcp_handshake.png")


# ============================================================
# Ch 21 PCIe —— 拓扑
# ============================================================
def ch21():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "PCIe 拓扑（第 21 章）")
    box(ax, 4.5, 5.5, 2, 1, "Root Complex\n(CPU+内存)", color="#e74c3c", fontsize=10)
    box(ax, 1.5, 3.5, 1.8, 1, "Switch", color="#9b59b6", fontsize=10)
    box(ax, 7.7, 3.5, 1.8, 1, "Switch", color="#9b59b6", fontsize=10)
    for i, (x, label) in enumerate([(0.2, "GPU"), (2.0, "NVMe"), (4.0, "Net"),
                                     (6.5, "Cam"), (8.5, "AI"), (10.0, "USB")]):
        c = "#3498db" if i < 3 else "#2ecc71"
        box(ax, x, 1.2, 1.3, 1, label, color=c, fontsize=10)
    # connections
    arrow(ax, 5.5, 5.5, 2.4, 4.5)
    arrow(ax, 5.5, 5.5, 8.6, 4.5)
    for x in [0.85, 2.65, 4.65]:
        arrow(ax, 2.4, 3.5, x, 2.2, style='-', color='#666')
    for x in [7.15, 9.15, 10.65]:
        arrow(ax, 8.6, 3.5, x, 2.2, style='-', color='#666')
    save(fig, "21_PCIe概念", "topology.png")


# ============================================================
# Ch 22 MIPI —— D-PHY HS/LP 切换
# ============================================================
def ch22():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 5), "MIPI D-PHY: LP → HS 切换（第 22 章）")
    # LP segment
    ax.fill_between([0.5, 3.5], 2, 3.5, color="#3498db", alpha=0.4)
    ax.text(2, 3.7, "LP (Low Power, 1.2V CMOS)", ha='center', fontsize=10, color='#2980b9', fontweight='bold')
    ax.text(2, 1.3, "握手序列\nLP-11→LP-01→LP-00", ha='center', fontsize=9, color='#555')
    # HS segment
    ax.fill_between([3.5, 9.0], 2.4, 3.1, color="#e74c3c", alpha=0.4)
    ax.text(6.25, 3.7, "HS (High Speed, 200 mV 差分, > 1 Gbps)", ha='center', fontsize=10, color='#c0392b', fontweight='bold')
    ax.text(6.25, 1.3, "数据传输", ha='center', fontsize=9, color='#555')
    # LP trail
    ax.fill_between([9.0, 10.5], 2, 3.5, color="#3498db", alpha=0.4)
    ax.text(9.75, 3.7, "LP\ntrail", ha='center', fontsize=9, color='#2980b9')
    save(fig, "22_MIPI_CSI_DSI", "d_phy_modes.png")


# ============================================================
# Ch 23 无线 —— 三家选型矩阵
# ============================================================
def ch23():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 7), "BLE / Wi-Fi / LoRa 三家定位（第 23 章）")
    # axes
    ax.annotate('', xy=(10.5, 1), xytext=(1, 1), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(10.7, 1, "距离", fontsize=11, va='center', fontweight='bold')
    ax.annotate('', xy=(1, 6.5), xytext=(1, 1), arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(1, 6.7, "速率", fontsize=11, ha='center', fontweight='bold')
    # points
    ax.scatter([2.5], [5.0], s=600, color="#3498db", alpha=0.7, edgecolor='black')
    ax.text(2.5, 5.6, "BLE\n10-100 m / 1-2 Mbps", ha='center', fontsize=10, fontweight='bold')
    ax.scatter([4.5], [6.0], s=600, color="#e74c3c", alpha=0.7, edgecolor='black')
    ax.text(4.5, 5.4, "Wi-Fi 6\n几十米 / 几百 Mbps", ha='center', fontsize=10, fontweight='bold')
    ax.scatter([9.0], [1.8], s=600, color="#2ecc71", alpha=0.7, edgecolor='black')
    ax.text(9.0, 2.5, "LoRa\n2-15 km / kbps", ha='center', fontsize=10, fontweight='bold')
    # power note
    ax.text(5.5, 0.3, "（圆圈大小 ≈ 功耗：BLE 与 LoRa 极低，Wi-Fi 高）",
            ha='center', fontsize=10, style='italic', color='#666')
    save(fig, "23_无线协议入门", "wireless_matrix.png")


# ============================================================
# Ch 24 RTOS 概念 —— 任务状态机
# ============================================================
def ch24():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "RTOS 任务状态机（第 24 章）")
    box(ax, 1, 5, 2, 1.2, "Ready", color="#2ecc71", fontsize=12)
    box(ax, 5, 5, 2, 1.2, "Running", color="#3498db", fontsize=12)
    box(ax, 9, 5, 2, 1.2, "Suspended", color="#95a5a6", fontsize=12)
    box(ax, 5, 1.5, 2, 1.2, "Blocked", color="#e67e22", fontsize=12)
    # arrows
    arrow(ax, 3, 5.6, 5, 5.6)
    ax.text(4, 5.9, "调度选中", fontsize=9, ha='center', color='#27ae60')
    arrow(ax, 5, 5.4, 3, 5.4)
    ax.text(4, 5.1, "时间片用完", fontsize=9, ha='center', color='#27ae60')
    arrow(ax, 6, 5, 6, 2.7, color='#e67e22')
    ax.text(6.5, 3.8, "等信号量/队列/延时", fontsize=9, color='#e67e22')
    arrow(ax, 5, 2.1, 1.8, 5, color='#e67e22')
    ax.text(2.6, 3.3, "事件来到", fontsize=9, color='#e67e22')
    arrow(ax, 7, 5.6, 9, 5.6, color='#95a5a6')
    ax.text(8, 5.9, "suspend", fontsize=9, ha='center', color='#666')
    save(fig, "24_RTOS概念与调度", "task_states.png")


# ============================================================
# Ch 25 mini RTOS —— 上下文切换
# ============================================================
def ch25():
    fig, ax = new_fig(11, 6.5)
    setup(ax, (0, 11), (0, 7), "上下文切换：SysTick + PendSV + PSP（第 25 章）")
    steps = [
        (0.3, "Task A 运行\n(thread + PSP)", "#3498db"),
        (2.5, "SysTick 触发\n(高优先级)", "#e67e22"),
        (4.6, "调度器选 Task B\n触发 PendSV", "#f39c12"),
        (7.0, "PendSV ISR\n保存 A.R4-R11\n切到 B 的 PSP\nPop B.R4-R11", "#9b59b6"),
        (9.5, "Task B 运行", "#2ecc71"),
    ]
    for x, s, c in steps:
        h = 2.2 if "PendSV ISR" in s else 1.5
        y = 3 if "PendSV ISR" in s else 3.3
        box(ax, x, y, 1.9, h, s, color=c, fontsize=9.5)
    for i in range(4):
        arrow(ax, 0.3 + 1.9 + 2.2*i, 4.1, 2.5 + 2.2*i, 4.1)
    ax.text(5.5, 0.7, "硬件帧 (R0-R3, R12, LR, PC, xPSR) 由 CPU 自动保存到 PSP",
            ha='center', fontsize=10, color='#27ae60',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#e8f5e9', edgecolor='#27ae60'))
    save(fig, "25_FreeRTOS实战", "context_switch.png")


# ============================================================
# Ch 26 Zephyr —— 子系统层次
# ============================================================
def ch26():
    fig, ax = new_fig(10, 7)
    setup(ax, (0, 10), (0, 8), "Zephyr 内核 + 子系统层次（第 26 章）")
    layers = [
        ("应用 (Application)", 7, "#e74c3c"),
        ("子系统 (Net / BLE / FS / USB / sensor / shell ...)", 5.7, "#9b59b6"),
        ("Device API (DT-based)", 4.4, "#3498db"),
        ("Drivers (GPIO / I2C / SPI / UART ...)", 3.1, "#2ecc71"),
        ("Zephyr 内核 (调度 + 同步 + 内存 + 中断)", 1.8, "#e67e22"),
        ("Arch 层 (ARM / RISC-V / x86 / Xtensa)", 0.5, "#34495e"),
    ]
    for label, y, c in layers:
        box(ax, 1, y, 8, 1.0, label, color=c, fontsize=10.5)
    save(fig, "26_Zephyr上手", "zephyr_layers.png")


# ============================================================
# Ch 27 实时性 —— 抖动来源
# ============================================================
def ch27():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "实时系统抖动来源（第 27 章）")
    # ideal timeline
    ax.plot([0.5, 10.5], [5.5, 5.5], 'b-', lw=2, alpha=0.6)
    ax.text(0.3, 5.5, "期望", ha='right', fontsize=10, va='center', color='blue')
    for x in [2, 4, 6, 8, 10]:
        ax.plot(x, 5.5, 'bo', markersize=10)
    # actual with jitter
    ax.plot([0.5, 10.5], [4.0, 4.0], 'r-', lw=2, alpha=0.6)
    ax.text(0.3, 4.0, "实际", ha='right', fontsize=10, va='center', color='red')
    for x in [2.1, 4.3, 5.8, 8.2, 9.9]:
        ax.plot(x, 4.0, 'ro', markersize=10)
    # sources
    sources = [
        ("OS 调度延迟", 1.5, "µs-ms"),
        ("ISR 嵌套 / 临界区", 3.0, "µs"),
        ("Cache miss", 4.5, "100 ns - µs"),
        ("DRAM 刷新", 6.0, "周期性 µs"),
        ("Bus 仲裁", 7.5, "ns - µs"),
        ("时钟源抖动", 9.0, "ppm"),
    ]
    for label, x, val in sources:
        ax.text(x, 2.0, f"• {label}\n  {val}", fontsize=9, color='#555', ha='center')
    save(fig, "27_实时性深入", "jitter_sources.png")


# ============================================================
# Ch 28 Linux 启动 —— 完整流程
# ============================================================
def ch28():
    fig, ax = new_fig(11, 8)
    setup(ax, (0, 11), (0, 9), "嵌入式 Linux 启动流程（第 28 章）")
    steps = [
        ("① 上电 / 复位\nCPU 从 BootROM 跑", "#e74c3c"),
        ("② SPL (一级 Bootloader)\n初始化 DDR", "#e67e22"),
        ("③ U-Boot\n加载 Kernel + DTB", "#f39c12"),
        ("④ Linux 内核\n初始化 + mount root", "#2ecc71"),
        ("⑤ init 系统\n(systemd / busybox)", "#3498db"),
        ("⑥ getty / login / shell", "#9b59b6"),
    ]
    for i, (s, c) in enumerate(steps):
        y = 7.5 - i * 1.2
        box(ax, 3, y, 5, 0.95, s, color=c, fontsize=10.5)
        if i < 5:
            arrow(ax, 5.5, y, 5.5, y - 0.25)
    save(fig, "28_启动流程", "boot_flow.png")


# ============================================================
# Ch 29 Buildroot —— 构建产物
# ============================================================
def ch29():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 6), "Buildroot 输出（第 29 章）")
    box(ax, 0.5, 2.5, 2.5, 1.5, "源码 + .config", color="#3498db", fontsize=10)
    box(ax, 4, 2.5, 2.5, 1.5, "Buildroot\n(make)", color="#e67e22", fontsize=11)
    box(ax, 7.5, 4, 3, 0.8, "zImage / 内核", color="#2ecc71", fontsize=10)
    box(ax, 7.5, 3, 3, 0.8, "*.dtb / 设备树", color="#27ae60", fontsize=10)
    box(ax, 7.5, 2, 3, 0.8, "rootfs.ext2 / 根文件系统", color="#1abc9c", fontsize=10)
    arrow(ax, 3, 3.25, 4, 3.25)
    for y in [4.4, 3.4, 2.4]:
        arrow(ax, 6.5, 3.25, 7.5, y)
    save(fig, "29_交叉编译_Buildroot", "buildroot_output.png")


# ============================================================
# Ch 30 设备树 —— 节点示意
# ============================================================
def ch30():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 8), "设备树结构（第 30 章）")
    box(ax, 4, 6.5, 3, 0.9, "/", color="#34495e", fontsize=11)
    box(ax, 0.3, 4.5, 2.5, 0.9, "cpus", color="#3498db", fontsize=10)
    box(ax, 3.5, 4.5, 2.5, 0.9, "memory@40000000", color="#2ecc71", fontsize=10)
    box(ax, 6.7, 4.5, 2.5, 0.9, "soc", color="#e67e22", fontsize=10)
    box(ax, 4, 2.5, 2.5, 0.9, "serial@10000000", color="#e74c3c", fontsize=10)
    box(ax, 7.5, 2.5, 2.5, 0.9, "gpio@10001000", color="#9b59b6", fontsize=10)
    # lines
    for x in [1.55, 4.75, 7.95]:
        arrow(ax, 5.5, 6.5, x, 5.4, style='-', color='#666')
    for x in [5.25, 8.75]:
        arrow(ax, 7.95, 4.5, x, 3.4, style='-', color='#666')
    # attribute snippet
    ax.text(5.5, 0.7,
            'compatible = "arm,pl011";\nreg = <0x10000000 0x1000>;\ninterrupts = <0 1 4>;',
            ha='center', fontsize=9, family='monospace', color='#333',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#fffacd', edgecolor='#999'))
    save(fig, "30_设备树", "dt_tree.png")


# ============================================================
# Ch 31 字符驱动 —— VFS 派发
# ============================================================
def ch31():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "字符设备：syscall → fops 派发（第 31 章）")
    box(ax, 0.5, 5, 2.5, 1.2, "用户进程\nread(fd,...)", color="#3498db", fontsize=10)
    box(ax, 4.0, 5, 2.5, 1.2, "VFS / 内核", color="#e67e22", fontsize=10)
    box(ax, 7.5, 5, 3.0, 1.2, "file_operations.read\n(驱动)", color="#e74c3c", fontsize=10)
    arrow(ax, 3.0, 5.6, 4.0, 5.6)
    arrow(ax, 6.5, 5.6, 7.5, 5.6)
    ax.text(5.5, 4.5, "syscall", fontsize=9, ha='center', color='#666', style='italic')
    ax.text(8.5, 4.5, "函数指针", fontsize=9, ha='center', color='#666', style='italic')
    # callback
    box(ax, 7.5, 2, 3.0, 1.5, "copy_to_user(buf, ...)\nreturn bytes", color="#9b59b6", fontsize=9.5)
    arrow(ax, 9.0, 5.0, 9.0, 3.5)
    ax.text(2, 1.5, "一切皆文件 = 一切走 file_operations 表",
            fontsize=11, color='#27ae60', fontweight='bold')
    save(fig, "31_字符设备驱动入门", "vfs_dispatch.png")


# ============================================================
# Ch 32 子系统驱动 —— device/driver/bus
# ============================================================
def ch32():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "Linux 设备模型：device / driver / bus（第 32 章）")
    box(ax, 4, 5.5, 3, 1, "bus_type", color="#e74c3c", fontsize=11)
    box(ax, 0.5, 3, 3, 1.5, "device 列表\n(设备实例)", color="#3498db", fontsize=10)
    box(ax, 7.5, 3, 3, 1.5, "driver 列表\n(驱动实例)", color="#2ecc71", fontsize=10)
    arrow(ax, 5.5, 5.5, 2.0, 4.5, color='#666', style='-')
    arrow(ax, 5.5, 5.5, 9.0, 4.5, color='#666', style='-')
    box(ax, 3.5, 0.5, 4, 1.2, "match() → probe()", color="#9b59b6", fontsize=11)
    arrow(ax, 3.5, 3, 4.5, 1.7, color='#9b59b6')
    arrow(ax, 7.5, 3, 6.5, 1.7, color='#9b59b6')
    save(fig, "32_子系统驱动模型", "device_driver_bus.png")


# ============================================================
# Ch 33 用户接口 —— 五条通道
# ============================================================
def ch33():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "用户态访问内核驱动的 5 条通道（第 33 章）")
    items = [
        ("/dev/xxx\n字节流", "#3498db"),
        ("sysfs\n一文件一值", "#2ecc71"),
        ("procfs\n旧式", "#95a5a6"),
        ("netlink\n事件推送", "#e67e22"),
        ("UIO/VFIO\n用户态驱动", "#9b59b6"),
    ]
    for i, (label, c) in enumerate(items):
        x = 0.3 + i * 2.15
        box(ax, x, 3, 1.95, 1.8, label, color=c, fontsize=10)
    ax.text(5.5, 1, "选择决策树见 README §33.8",
            ha='center', fontsize=10, color='#666', style='italic')
    save(fig, "33_用户态接口", "user_interfaces.png")


# ============================================================
# Ch 34 调试 —— 工具地图
# ============================================================
def ch34():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "嵌入式 Linux 调试工具地图（第 34 章）")
    # User-space tools
    ax.text(2.5, 6, "用户态", fontsize=12, fontweight='bold', color='#3498db')
    for i, t in enumerate(["top/htop", "strace", "ltrace", "gdb"]):
        box(ax, 0.3 + (i%2)*2.5, 4.0 - (i//2)*1.0, 2.2, 0.7, t, color="#3498db", fontsize=10)
    # Kernel tools
    ax.text(8.5, 6, "内核态 / 跨层", fontsize=12, fontweight='bold', color='#e74c3c')
    for i, t in enumerate(["dmesg / /proc/interrupts", "ftrace + tracepoint", "perf + flamegraph",
                            "bpftrace / eBPF", "kgdb / crash"]):
        y = 4.7 - i * 0.85
        box(ax, 6.0, y, 4.7, 0.7, t, color="#e74c3c", fontsize=10)
    save(fig, "34_调试与性能", "debug_tools.png")


# ============================================================
# Ch 35 Verilog —— 计数器波形
# ============================================================
def ch35():
    import numpy as np
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 6), "4 位计数器仿真波形（第 35 章）")
    # CLK
    pts_x = np.arange(0, 11, 0.5)
    pts_y = [3.5 if (i % 2 == 0) else 4.2 for i in range(len(pts_x))]
    ax.step(pts_x, pts_y, 'b-', lw=1.5, where='post')
    ax.text(-0.2, 3.85, "CLK", fontsize=11, ha='right', fontweight='bold')
    # rst_n
    ax.plot([0, 1, 1, 11], [1.5, 1.5, 2.5, 2.5], 'k-', lw=1.5)
    ax.text(-0.2, 2.0, "rst_n", fontsize=11, ha='right', fontweight='bold')
    # cnt
    cnts = ['0', '1', '2', '3', '4', '5']
    ax.text(-0.2, 0.5, "cnt", fontsize=11, ha='right', fontweight='bold')
    for i, c in enumerate(cnts):
        x = 1.5 + i * 1.6
        ax.fill_between([x, x + 1.6], 0.2, 0.9, color="#2ecc71", alpha=0.4)
        ax.text(x + 0.8, 0.55, c, ha='center', va='center', fontsize=11, fontweight='bold')
    save(fig, "35_Verilog入门", "counter_waveform.png")


# ============================================================
# Ch 36 FSM —— 三段式 UART RX 状态机
# ============================================================
def ch36():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "UART RX 状态机（第 36 章）")
    states = [
        ("IDLE", 1.5, 4, "#3498db"),
        ("START", 4, 4, "#e67e22"),
        ("SAMPLE", 6.5, 4, "#2ecc71"),
        ("STOP", 9, 4, "#9b59b6"),
    ]
    for label, x, y, c in states:
        circle = Circle((x, y), 0.8, facecolor=c, alpha=0.8, edgecolor='black')
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, color='white', fontweight='bold')
    # arrows
    arrow(ax, 2.3, 4, 3.2, 4)
    ax.text(2.75, 4.4, "rx=0", fontsize=9, ha='center', color='#666')
    arrow(ax, 4.8, 4, 5.7, 4)
    ax.text(5.25, 4.4, "中点确认", fontsize=9, ha='center', color='#666')
    arrow(ax, 7.3, 4, 8.2, 4)
    ax.text(7.75, 4.4, "8 bits 完", fontsize=9, ha='center', color='#666')
    # loop back
    ax.annotate('', xy=(1.5, 4.8), xytext=(9, 4.8),
                arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=-0.4",
                                color='#666'))
    ax.text(5.25, 6, "完成一帧 (valid 拉高 1 拍)", fontsize=10, ha='center', color='#27ae60')
    # 3-process note
    ax.text(5.5, 1.5,
            "三段式 = 状态寄存器(时序) + 转移逻辑(组合) + 输出(组合)",
            ha='center', fontsize=10, color='#555',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#fff9e6', edgecolor='#999'))
    save(fig, "36_FSM", "uart_rx_fsm.png")


# ============================================================
# Ch 37 片上总线 —— SoC 分层
# ============================================================
def ch37():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 8), "SoC 总线分层：AXI / AHB / APB（第 37 章）")
    box(ax, 0.5, 6.5, 2, 0.9, "CPU", color="#e74c3c", fontsize=11)
    box(ax, 3.5, 6.5, 2.5, 0.9, "DDR Controller", color="#9b59b6", fontsize=10)
    box(ax, 6.5, 6.5, 2.5, 0.9, "GPU / DMA", color="#3498db", fontsize=10)
    # AXI bar
    box(ax, 0.5, 5.5, 9.5, 0.6, "AXI Interconnect (高性能)", color="#e74c3c", text_color="white", fontsize=10)
    # bridge
    box(ax, 1, 4.2, 4, 0.7, "AXI → AHB Bridge", color="#34495e", fontsize=10)
    # AHB
    box(ax, 0.5, 3.2, 9.5, 0.6, "AHB Interconnect (中等)", color="#e67e22", fontsize=10)
    box(ax, 0.5, 2.2, 2.5, 0.7, "Ethernet", color="#f39c12", fontsize=10)
    box(ax, 3.5, 2.2, 2.5, 0.7, "USB", color="#f39c12", fontsize=10)
    # bridge
    box(ax, 6, 2.2, 4, 0.7, "AHB → APB Bridge", color="#34495e", fontsize=10)
    # APB
    box(ax, 0.5, 1.2, 9.5, 0.6, "APB Interconnect (低速)", color="#2ecc71", fontsize=10)
    for i, n in enumerate(["UART", "SPI", "I²C", "GPIO", "Timer"]):
        box(ax, 0.5 + i*1.9, 0.2, 1.7, 0.7, n, color="#27ae60", fontsize=10)
    save(fig, "37_片上总线", "soc_bus_hierarchy.png")


# ============================================================
# Ch 38 SoC 集成 —— 异构多核
# ============================================================
def ch38():
    fig, ax = new_fig(11, 7)
    setup(ax, (0, 11), (0, 8), "异构多核 SoC（第 38 章）")
    box(ax, 0.5, 5.5, 3, 1.5, "Cortex-A 集群\n跑 Linux + 应用", color="#e74c3c", fontsize=10)
    box(ax, 4, 5.5, 3, 1.5, "Cortex-R / M\n跑 RTOS + 实时控制", color="#3498db", fontsize=10)
    box(ax, 7.5, 5.5, 3, 1.5, "AI / GPU / NPU\n加速器", color="#9b59b6", fontsize=10)
    box(ax, 0.5, 3, 10, 1.2, "Cache Coherent Interconnect (AXI / CCI / CMN)", color="#34495e", fontsize=11)
    box(ax, 0.5, 1, 3, 1.2, "DRAM", color="#2ecc71", fontsize=11)
    box(ax, 4, 1, 3, 1.2, "外设域\n(USB/Ethernet/SPI)", color="#e67e22", fontsize=10)
    box(ax, 7.5, 1, 3, 1.2, "安全岛\n(TrustZone + SE)", color="#1abc9c", fontsize=10)
    save(fig, "38_集成软核SoC", "heterogeneous_soc.png")


# ============================================================
# Ch 39 FPGA —— 七步流程
# ============================================================
def ch39():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "FPGA 设计流程七步（第 39 章）")
    steps = [
        "1. RTL 编写", "2. 功能仿真", "3. 综合 (Synth)",
        "4. 布局布线 (P&R)", "5. 时序分析 (STA)",
        "6. 时序仿真", "7. Bitstream + 下载"
    ]
    colors = ["#3498db", "#9b59b6", "#e67e22", "#f39c12", "#e74c3c", "#2ecc71", "#1abc9c"]
    for i, (s, c) in enumerate(zip(steps, colors)):
        x = 0.3 + (i % 4) * 2.7
        y = 4.5 - (i // 4) * 2
        box(ax, x, y, 2.4, 1.3, s, color=c, fontsize=10)
    save(fig, "39_FPGA验证", "fpga_flow.png")


# ============================================================
# Ch 40 安全 —— 信任链
# ============================================================
def ch40():
    fig, ax = new_fig(10, 7)
    setup(ax, (0, 10), (0, 8), "Secure Boot 信任链（第 40 章）")
    levels = [
        ("应用 (易变)", 7, "#bdc3c7"),
        ("操作系统", 5.8, "#3498db"),
        ("U-Boot / Bootloader", 4.6, "#e67e22"),
        ("SPL", 3.4, "#f39c12"),
        ("BootROM (固化)", 2.2, "#e74c3c"),
        ("Root of Trust (OTP 公钥)", 1.0, "#2ecc71"),
    ]
    for label, y, c in levels:
        box(ax, 2, y, 6, 1.0, label, color=c, fontsize=11)
    for y in [1.0, 2.2, 3.4, 4.6, 5.8]:
        arrow(ax, 8.5, y + 0.5, 8.5, y + 1.5, color='#27ae60')
        ax.text(8.7, y + 1.0, "验签", fontsize=9, color='#27ae60', fontweight='bold')
    save(fig, "40_嵌入式安全", "trust_chain.png")


# ============================================================
# Ch 41 低功耗 —— 模式电流
# ============================================================
def ch41():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 6), "MCU 低功耗模式电流（对数刻度，第 41 章）")
    modes = [
        ("Run",       5.0, "几 mA - 几十 mA", "#e74c3c"),
        ("Sleep",     4.0, "几百 µA - mA",     "#e67e22"),
        ("Stop",      3.0, "几十 µA",           "#f39c12"),
        ("Standby",   2.0, "几 µA",             "#2ecc71"),
        ("Shutdown",  1.0, "< 1 µA",            "#3498db"),
    ]
    for label, x_pos, val, c in modes:
        x = 0.3 + (x_pos - 1) * 2
        box(ax, x, 2.5, 1.7, 1.2, label, color=c, fontsize=11)
        ax.text(x + 0.85, 1.7, val, ha='center', fontsize=10, color='#333')
    ax.annotate('', xy=(9.5, 2.0), xytext=(1.5, 2.0),
                arrowprops=dict(arrowstyle='->', color='#27ae60', lw=2))
    ax.text(5.5, 1.0, "电流相差 1000×", ha='center', fontsize=11, color='#27ae60', fontweight='bold')
    save(fig, "41_低功耗设计", "power_modes.png")


# ============================================================
# Ch 42 OTA —— A/B 分区
# ============================================================
def ch42():
    fig, ax = new_fig(11, 5)
    setup(ax, (0, 11), (0, 6), "A/B 分区 OTA 升级（第 42 章）")
    box(ax, 0.3, 3, 2.5, 1.5, "Bootloader\n(不可改)", color="#34495e", fontsize=10)
    box(ax, 3.3, 3, 3.5, 1.5, "分区 A\n当前运行", color="#2ecc71", fontsize=11)
    box(ax, 7.3, 3, 3.5, 1.5, "分区 B\n下载新固件", color="#e67e22", fontsize=11)
    # arrows
    ax.text(5.5, 1.5, "1. 下载到 B  →  2. 验签  →  3. 标记下次启动 B  →  4. 重启  →  5. B 健康检查\n失败 → bootloader 自动回 A",
            ha='center', fontsize=10, color='#333',
            bbox=dict(boxstyle="round,pad=0.5", facecolor='#fff3e0', edgecolor='#e67e22'))
    save(fig, "42_OTA_固件升级", "ab_partition.png")


# ============================================================
# Ch 43 边缘 AI —— 工作流
# ============================================================
def ch43():
    fig, ax = new_fig(11, 6)
    setup(ax, (0, 11), (0, 7), "边缘 AI 部署工作流（第 43 章）")
    steps = [
        ("训练 (FP32)\nPyTorch / TF", "#9b59b6"),
        ("量化 (int8)\nQAT / PTQ", "#3498db"),
        ("转换 TFLite", "#2ecc71"),
        ("生成 model.cc", "#e67e22"),
        ("编进 MCU 固件\n+ CMSIS-NN 加速", "#e74c3c"),
    ]
    for i, (s, c) in enumerate(steps):
        x = 0.3 + i * 2.15
        box(ax, x, 3, 1.95, 1.5, s, color=c, fontsize=10)
        if i < len(steps) - 1:
            arrow(ax, x + 1.95, 3.75, x + 2.15, 3.75)
    ax.text(5.5, 1.3, "MCU 端：64 KB SRAM 上能跑 MobileNet 0.25× 缩水版",
            ha='center', fontsize=10.5, color='#27ae60', fontweight='bold')
    save(fig, "43_边缘AI", "edge_ai_workflow.png")


# ============================================================
# Ch 44 功能安全 —— ASIL 等级
# ============================================================
def ch44():
    fig, ax = new_fig(10, 6)
    setup(ax, (0, 10), (0, 6), "ISO 26262 ASIL 等级（第 44 章）")
    levels = [
        ("ASIL A", "后视镜调节", 1.0, "#bdc3c7"),
        ("ASIL B", "仪表盘", 3.0, "#3498db"),
        ("ASIL C", "部分驾驶辅助", 5.0, "#e67e22"),
        ("ASIL D", "刹车 / 转向 / 动力", 7.0, "#e74c3c"),
    ]
    for label, app, x, c in levels:
        box(ax, x, 2.5, 1.8, 1.5, label, color=c, fontsize=12)
        ax.text(x + 0.9, 2.0, app, ha='center', fontsize=9.5, color='#333')
    ax.annotate('', xy=(9, 4.5), xytext=(1, 4.5),
                arrowprops=dict(arrowstyle='->', color='#c0392b', lw=2))
    ax.text(5, 4.8, "风险越高 → 要求越严", ha='center', fontsize=11, color='#c0392b', fontweight='bold')
    save(fig, "44_功能安全与编码规范", "asil_levels.png")


# ============================================================
# Ch 45 Embedded Rust —— 层次
# ============================================================
def ch45():
    fig, ax = new_fig(10, 7)
    setup(ax, (0, 10), (0, 8), "Embedded Rust 层次（第 45 章）")
    layers = [
        ("应用 (Application)", 7, "#e74c3c"),
        ("BSP (Board Support Package)", 5.8, "#9b59b6"),
        ("HAL (Hardware Abstraction Layer)\nembedded-hal traits", 4.4, "#3498db"),
        ("PAC (Peripheral Access Crate)\n按 SVD 生成的安全寄存器结构体", 2.9, "#2ecc71"),
        ("cortex-m / riscv runtime + 启动 crate", 1.5, "#e67e22"),
    ]
    for label, y, c in layers:
        box(ax, 1, y, 8, 1.0, label, color=c, fontsize=11)
    save(fig, "45_Embedded_Rust", "rust_layers.png")


# ============================================================
# Main dispatcher
# ============================================================
ALL_FUNCS = {
    "ch00": ch00, "ch01": ch01, "ch02": ch02, "ch03": ch03, "ch04": ch04,
    "ch05": ch05, "ch06": ch06, "ch07": ch07, "ch08": ch08, "ch09": ch09,
    "ch10": ch10, "ch11": ch11, "ch12": ch12, "ch13": ch13, "ch14": ch14,
    "ch15": ch15, "ch16": ch16, "ch17": ch17, "ch18": ch18, "ch19": ch19,
    "ch20": ch20, "ch21": ch21, "ch22": ch22, "ch23": ch23, "ch24": ch24,
    "ch25": ch25, "ch26": ch26, "ch27": ch27, "ch28": ch28, "ch29": ch29,
    "ch30": ch30, "ch31": ch31, "ch32": ch32, "ch33": ch33, "ch34": ch34,
    "ch35": ch35, "ch36": ch36, "ch37": ch37, "ch38": ch38, "ch39": ch39,
    "ch40": ch40, "ch41": ch41, "ch42": ch42, "ch43": ch43, "ch44": ch44,
    "ch45": ch45,
}

CHAPTER_ASSETS = {
    "ch00": ("00_导论", "hardware_layers.png"),
    "ch01": ("01_数字与逻辑基础", "dff_timing.png"),
    "ch02": ("02_计算机体系结构速通", "memory_hierarchy.png"),
    "ch03": ("03_C语言再训练", "memory_layout.png"),
    "ch04": ("04_电子电路最小集", "push_pull_vs_open_drain.png"),
    "ch05": ("05_数字电路与时序", "two_flop_synchronizer.png"),
    "ch06": ("06_总线与时序图", "valid_ready_handshake.png"),
    "ch07": ("07_QEMU与工具链搭建", "toolchain_flow.png"),
    "ch08": ("08_ARM_Cortex_M_架构", "memory_map.png"),
    "ch09": ("09_启动文件与链接脚本", "vma_lma.png"),
    "ch10": ("10_第一个程序_GPIO", "uart_init_steps.png"),
    "ch11": ("11_中断与异常", "isr_entry_flow.png"),
    "ch12": ("12_定时器与SysTick", "systick_periodic.png"),
    "ch13": ("13_DMA", "ping_pong.png"),
    "ch14": ("14_ADC_DAC", "nyquist.png"),
    "ch15": ("15_UART", "uart_frame.png"),
    "ch16": ("16_SPI", "spi_modes.png"),
    "ch17": ("17_I2C_SMBus", "arbitration.png"),
    "ch18": ("18_CAN_CANFD", "can_frame_layout.png"),
    "ch19": ("19_USB概览", "enumeration.png"),
    "ch20": ("20_Ethernet_TCPIP", "tcp_handshake.png"),
    "ch21": ("21_PCIe概念", "topology.png"),
    "ch22": ("22_MIPI_CSI_DSI", "d_phy_modes.png"),
    "ch23": ("23_无线协议入门", "wireless_matrix.png"),
    "ch24": ("24_RTOS概念与调度", "task_states.png"),
    "ch25": ("25_FreeRTOS实战", "context_switch.png"),
    "ch26": ("26_Zephyr上手", "zephyr_layers.png"),
    "ch27": ("27_实时性深入", "jitter_sources.png"),
    "ch28": ("28_启动流程", "boot_flow.png"),
    "ch29": ("29_交叉编译_Buildroot", "buildroot_output.png"),
    "ch30": ("30_设备树", "dt_tree.png"),
    "ch31": ("31_字符设备驱动入门", "vfs_dispatch.png"),
    "ch32": ("32_子系统驱动模型", "device_driver_bus.png"),
    "ch33": ("33_用户态接口", "user_interfaces.png"),
    "ch34": ("34_调试与性能", "debug_tools.png"),
    "ch35": ("35_Verilog入门", "counter_waveform.png"),
    "ch36": ("36_FSM", "uart_rx_fsm.png"),
    "ch37": ("37_片上总线", "soc_bus_hierarchy.png"),
    "ch38": ("38_集成软核SoC", "heterogeneous_soc.png"),
    "ch39": ("39_FPGA验证", "fpga_flow.png"),
    "ch40": ("40_嵌入式安全", "trust_chain.png"),
    "ch41": ("41_低功耗设计", "power_modes.png"),
    "ch42": ("42_OTA_固件升级", "ab_partition.png"),
    "ch43": ("43_边缘AI", "edge_ai_workflow.png"),
    "ch44": ("44_功能安全与编码规范", "asil_levels.png"),
    "ch45": ("45_Embedded_Rust", "rust_layers.png"),
}

def write_chapter_sources(targets):
    for target in targets:
        chapter_dir, image_name = CHAPTER_ASSETS[target]
        src_dir = Path(BASE) / chapter_dir / "images" / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        script_path = src_dir / "generate_diagram.py"
        script_path.write_text(
            f'''#!/usr/bin/env python3
"""Generate {image_name} for this chapter.

This chapter-local entry point keeps the drawing source next to the image while
reusing the shared visual helpers in scripts/gen_diagrams.py.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.gen_diagrams import {target}


if __name__ == "__main__":
    {target}()
''',
            encoding="utf-8",
        )
        print(f"  -> {chapter_dir}/images/src/generate_diagram.py")

def update_readmes(targets):
    for target in targets:
        chapter_dir, image_name = CHAPTER_ASSETS[target]
        readme = Path(BASE) / chapter_dir / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8")
        image_ref = f"images/{image_name}"
        if image_ref in text:
            continue
        alt = f"{chapter_dir.split('_', 1)[-1]}配图"
        block = f"![{alt}]({image_ref})\n\n"
        marker = "---\n\n"
        if marker in text:
            text = text.replace(marker, marker + block, 1)
        else:
            lines = text.splitlines(keepends=True)
            insert_at = 1 if lines else 0
            lines[insert_at:insert_at] = ["\n", block]
            text = "".join(lines)
        readme.write_text(text, encoding="utf-8")
        print(f"  -> {chapter_dir}/README.md")

if __name__ == "__main__":
    update_md = "--update-readmes" in sys.argv
    raw_targets = [arg for arg in sys.argv[1:] if arg != "--update-readmes"]
    targets = raw_targets if raw_targets else list(ALL_FUNCS.keys())
    for t in targets:
        if t in ALL_FUNCS:
            print(f"[{t}] generating...")
            ALL_FUNCS[t]()
        else:
            print(f"[!] unknown target: {t}")
    valid_targets = [t for t in targets if t in ALL_FUNCS]
    print("[sources] writing chapter-local generators...")
    write_chapter_sources(valid_targets)
    if update_md:
        print("[readmes] inserting diagram references...")
        update_readmes(valid_targets)
    print("Done.")
