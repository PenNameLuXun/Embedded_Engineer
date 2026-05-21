# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 45-chapter embedded systems engineering curriculum (textbook + runnable code). Chapter names and README content are in Simplified Chinese; code comments are often bilingual. The project has no runtime application — it is a structured learning resource.

## Building Code Examples

Each chapter's `code/` subdirectory is self-contained. Navigate to the specific example directory and use `make`:

```bash
# Build
make

# Run on QEMU (ARM Cortex-M examples)
make run

# Debug with GDB
make debug

# Simulate Verilog
make sim       # iverilog + vvp
make wave      # gtkwave waveform viewer
```

### Required Toolchains

- **ARM Cortex-M**: `gcc-arm-none-eabi`, `qemu-system-arm`, `gdb-multiarch`
- **Verilog/HDL**: `iverilog`, `gtkwave`, `verilator`
- **RISC-V** (some chapters): `gcc-riscv64-unknown-elf`
- **Linux kernel modules**: standard kernel headers + `make -C /lib/modules/$(uname -r)/build`

### QEMU Target

All MCU examples target `qemu-system-arm -M lm3s6965evb` or `mps2-an385` (ARM Cortex-M3). Flash starts at `0x00000000`, SRAM at `0x20000000`.

## Diagram Generation

Chapter diagrams are generated from Python scripts using matplotlib:

```bash
# Regenerate all diagrams
python3 scripts/gen_diagrams.py

# Regenerate specific chapters
python3 scripts/gen_diagrams.py ch02 ch18

# Per-chapter: diagrams live in NN_ChapterName/images/src/
python3 NN_ChapterName/images/src/generate_diagram.py
```

Diagrams are committed as PNG files under `images/`. The Python source scripts are under `images/src/`.

## Repository Structure

Every chapter follows the same layout:

```
NN_ChapterName/
├── README.md          # Textbook chapter content (Chinese, 2000–5000 words)
├── images/            # Generated PNG diagrams
│   └── src/           # Python generation scripts (matplotlib)
└── code/
    ├── 0X_example/
    │   ├── *.c / *.h  # C source
    │   ├── *.s        # ARM assembly (startup, vector table)
    │   ├── *.ld       # Linker script
    │   ├── *.v        # Verilog HDL
    │   └── Makefile
    └── answers.md
```

Chapters 00–06: digital logic, computer architecture, circuits, timing
Chapters 07–14: ARM Cortex-M bare-metal (startup, GPIO, UART, interrupts, timers, DMA, ADC/DAC)
Chapters 15–23: communication protocols (UART, SPI, I2C, CAN, USB, Ethernet, PCIe, MIPI, wireless)
Chapters 24–27: RTOS (mini-RTOS from scratch, FreeRTOS, Zephyr, real-time analysis)
Chapters 28–34: embedded Linux (boot, Buildroot, device trees, character drivers, subsystem drivers)
Chapters 35–39: HDL/FPGA/SoC (Verilog, FSM, AXI/AHB/APB, SoC integration, FPGA verification)
Chapters 40–45: security, low-power, OTA, edge AI, functional safety, Embedded Rust

See `ROADMAP.md` for the complete chapter index and three recommended learning paths (MCU engineer, Linux embedded, IC/FPGA).

## Bare-Metal Code Conventions

- **Startup sequence**: assembly `.s` file sets up vector table, stack pointer, copies `.data`, zeros `.bss`, then calls `main`
- **Register access**: direct memory-mapped I/O via `volatile uint32_t *` casts or `#define REG (*(volatile uint32_t*)ADDR)`
- **No standard library by default**: newlib-nano (`--specs=nano.specs`) used only where printf is needed
- **Linker scripts**: define `FLASH` and `SRAM` regions; output sections: `.text`, `.data`, `.bss`, `.stack`

## Build Artifacts (gitignored)

`*.o`, `*.elf`, `*.bin`, `*.hex`, `*.map`, `*.vvp`, `*.vcd`, `*.ko`, `build/`, `output/`, `obj_dir/`
