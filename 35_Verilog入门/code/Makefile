IVERILOG ?= iverilog
VVP      ?= vvp

.PHONY: all clean
all: wave.vcd

sim: tb_counter4.v counter4.v
	$(IVERILOG) -o $@ tb_counter4.v counter4.v

wave.vcd: sim
	$(VVP) sim

clean:
	rm -f sim wave.vcd
