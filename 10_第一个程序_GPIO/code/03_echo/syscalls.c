#include <sys/stat.h>
#include <stdint.h>
#include "uart.h"

int _write(int fd, const char *buf, int len)
{
    (void)fd;
    for (int i = 0; i < len; i++) uart0_putc(buf[i]);
    return len;
}

int _read(int fd, char *buf, int len)   { (void)fd;(void)buf;(void)len; return 0; }
int _close(int fd)                       { (void)fd; return -1; }
int _lseek(int fd, int p, int w)         { (void)fd;(void)p;(void)w; return 0; }
int _fstat(int fd, struct stat *st)      { (void)fd; st->st_mode = S_IFCHR; return 0; }
int _isatty(int fd)                      { (void)fd; return 1; }
int _getpid(void)                        { return 1; }
int _kill(int pid, int sig)              { (void)pid;(void)sig; return -1; }

extern uint8_t _end;
static uint8_t *heap_end;
void *_sbrk(int incr) {
    if (!heap_end) heap_end = &_end;
    uint8_t *prev = heap_end;
    heap_end += incr;
    return prev;
}

void SystemInit(void) { /* QEMU 不需要时钟配置 */ }
