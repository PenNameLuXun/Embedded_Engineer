IVERILOG ?= iverilog
VVP      ?= vvp

.PHONY: all clean
all: wave.vcd

uart_tx.vvp: uart_tx.v tb_uart_tx.v
	$(IVERILOG) -o $@ tb_uart_tx.v uart_tx.v

wave.vcd: uart_tx.vvp
	$(VVP) $<

clean:
	rm -f *.vvp wave.vcd
