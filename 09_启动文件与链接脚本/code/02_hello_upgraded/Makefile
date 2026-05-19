TARGET   = hello2
PREFIX   = arm-none-eabi-
CC       = $(PREFIX)gcc
SIZE     = $(PREFIX)size
OBJDUMP  = $(PREFIX)objdump

CFLAGS   = -mcpu=cortex-m3 -mthumb -ffreestanding \
           -Wall -Wextra -O0 -g
LDFLAGS  = -T linker.ld --specs=nano.specs \
           -Wl,--gc-sections -Wl,-Map=$(TARGET).map

OBJS = main.o syscalls.o startup.o

.PHONY: all run size dis clean

all: $(TARGET).elf

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.s
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET).elf: $(OBJS) linker.ld
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJS)

run: $(TARGET).elf
	qemu-system-arm -M lm3s6965evb -nographic -kernel $<

size: $(TARGET).elf
	$(SIZE) $<

dis: $(TARGET).elf
	$(OBJDUMP) -d $< | less

clean:
	rm -f *.o *.elf *.map
