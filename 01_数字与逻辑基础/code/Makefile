# 第 01 章 代码示例 Makefile
#
# 目标：
#   make run-bitops   编译并运行 C 位运算演示
#   make run-hdl      用 iverilog 编译 + vvp 仿真 半加器
#   make clean

CC      ?= gcc
CFLAGS  ?= -std=c11 -Wall -Wextra -O2

IVERILOG ?= iverilog
VVP      ?= vvp

.PHONY: all run-bitops run-hdl clean

all: bitops half_adder.vvp

# -------- C 部分 --------
bitops: bitops.c
	$(CC) $(CFLAGS) -o $@ $<

run-bitops: bitops
	@echo "=========================================="
	@echo "  位运算演示 (对应 README §1.3)"
	@echo "=========================================="
	./bitops

# -------- Verilog 部分 --------
half_adder.vvp: half_adder.v
	$(IVERILOG) -o $@ $<

run-hdl: half_adder.vvp
	@echo "=========================================="
	@echo "  半加器仿真 (对应 README §1.6)"
	@echo "=========================================="
	$(VVP) $<
	@echo ""
	@echo "波形已写入 wave.vcd，可用：gtkwave wave.vcd 查看"

clean:
	rm -f bitops half_adder.vvp wave.vcd
