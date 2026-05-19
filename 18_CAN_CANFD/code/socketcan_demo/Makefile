CC      ?= gcc
CFLAGS  ?= -Wall -Wextra -O2

.PHONY: all clean
all: sender receiver

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f sender receiver
