#include "led.h"
#include "regs.h"

void led_init(void)
{
    SYSCTL_RCGC2 |= RCGC2_GPIOF;
    GPIOF_DIR    |= (1u << 0);
    GPIOF_DEN    |= (1u << 0);
}

void led_set(int on)
{
    if (on) GPIOF_DATA |=  (1u << 0);
    else    GPIOF_DATA &= ~(1u << 0);
}
