IVERILOG ?= iverilog
VVP      ?= vvp

.PHONY: all clean

all: spi_master.vcd

spi_master.vvp: spi_master.v
	$(IVERILOG) -o $@ $<

spi_master.vcd: spi_master.vvp
	$(VVP) $<

clean:
	rm -f spi_master.vvp spi_master.vcd
