CC      ?= gcc
CFLAGS  ?= -std=c11 -Wall -Wextra
LDFLAGS ?= -lpthread

.PHONY: all run show-volatile clean

all: mem_layout struct_pad atomic_race

mem_layout: mem_layout.c
	$(CC) $(CFLAGS) -O0 -o $@ $<

struct_pad: struct_pad.c
	$(CC) $(CFLAGS) -O0 -o $@ $<

atomic_race: atomic_race.c
	$(CC) $(CFLAGS) -O2 -o $@ $< $(LDFLAGS)

show-volatile: volatile_demo.c volatile_extern.c
	@echo "=== -O2 编译 volatile_demo.c 的汇编 ==="
	@$(CC) $(CFLAGS) -O2 -S -o - volatile_demo.c | \
	  sed -n '/wait_v:/,/\.size.*wait_v/p; /wait_nv:/,/\.size.*wait_nv/p'
	@echo ""
	@echo "看 wait_nv: 循环里只读一次内存就跳到自己（死循环）"
	@echo "看 wait_v : 每次循环都重新加载，反映出 volatile 的作用"

clean:
	rm -f mem_layout struct_pad atomic_race
