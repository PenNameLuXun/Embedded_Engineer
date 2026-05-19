TARGET   = hello
PREFIX   = arm-none-eabi-
CC       = $(PREFIX)gcc
OBJCOPY  = $(PREFIX)objcopy

CFLAGS   = -mcpu=cortex-m3 -mthumb -nostdlib -ffreestanding \
           -Wall -Wextra -O0 -g
LDFLAGS  = -T linker.ld -nostdlib -Wl,-Map=$(TARGET).map

OBJS = hello.o startup.o

.PHONY: all run debug clean

all: $(TARGET).elf

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.s
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET).elf: $(OBJS) linker.ld
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJS)

run: $(TARGET).elf
	qemu-system-arm -M lm3s6965evb -nographic -kernel $<

debug: $(TARGET).elf
	@echo "另开一个终端跑：gdb-multiarch -ex 'target remote :1234' -ex 'file $(TARGET).elf'"
	qemu-system-arm -M lm3s6965evb -nographic -kernel $< -s -S

clean:
	rm -f *.o *.elf *.map
