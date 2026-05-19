/* LM3S6965 寄存器（用到的部分） */
#pragma once
#include <stdint.h>

/* ---- SysCtl ---- */
#define SYSCTL_RCGC1   (*(volatile uint32_t *)0x400FE104u)
#define SYSCTL_RCGC2   (*(volatile uint32_t *)0x400FE108u)
#define RCGC1_UART0    (1u << 0)
#define RCGC2_GPIOA    (1u << 0)
#define RCGC2_GPIOF    (1u << 5)

/* ---- GPIO Port F ---- */
#define GPIOF_BASE     0x40025000u
#define GPIOF_DATA     (*(volatile uint32_t *)(GPIOF_BASE + 0x3FCu))
#define GPIOF_DIR      (*(volatile uint32_t *)(GPIOF_BASE + 0x400u))
#define GPIOF_DEN      (*(volatile uint32_t *)(GPIOF_BASE + 0x51Cu))

/* ---- GPIO Port A ---- */
#define GPIOA_BASE     0x40004000u
#define GPIOA_DEN      (*(volatile uint32_t *)(GPIOA_BASE + 0x51Cu))
#define GPIOA_AFSEL    (*(volatile uint32_t *)(GPIOA_BASE + 0x420u))

/* ---- UART0 ---- */
#define UART0_BASE     0x4000C000u
#define UART0_DR       (*(volatile uint32_t *)(UART0_BASE + 0x000u))
#define UART0_FR       (*(volatile uint32_t *)(UART0_BASE + 0x018u))
#define UART0_IBRD     (*(volatile uint32_t *)(UART0_BASE + 0x024u))
#define UART0_FBRD     (*(volatile uint32_t *)(UART0_BASE + 0x028u))
#define UART0_LCRH     (*(volatile uint32_t *)(UART0_BASE + 0x02Cu))
#define UART0_CTL      (*(volatile uint32_t *)(UART0_BASE + 0x030u))
#define UART0_IM       (*(volatile uint32_t *)(UART0_BASE + 0x038u))
#define UART0_ICR      (*(volatile uint32_t *)(UART0_BASE + 0x044u))

#define UART0_FR_RXFE      (1u << 4)
#define UART0_FR_TXFF      (1u << 5)
#define UART0_LCRH_WLEN_8  (3u << 5)
#define UART0_LCRH_FEN     (1u << 4)
#define UART0_CTL_UARTEN   (1u << 0)
#define UART0_CTL_TXE      (1u << 8)
#define UART0_CTL_RXE      (1u << 9)
