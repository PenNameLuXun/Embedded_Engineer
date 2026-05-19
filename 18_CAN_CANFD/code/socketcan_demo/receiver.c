/*
 * SocketCAN 接收演示。
 *   ./receiver vcan0
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int main(int argc, char *argv[])
{
    const char *ifname = (argc > 1) ? argv[1] : "vcan0";

    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) { perror("socket"); return 1; }

    struct ifreq ifr;
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ioctl(s, SIOCGIFINDEX, &ifr);

    struct sockaddr_can addr = { .can_family = AF_CAN,
                                 .can_ifindex = ifr.ifr_ifindex };
    bind(s, (struct sockaddr *)&addr, sizeof(addr));

    printf("listening on %s ...\n", ifname);
    while (1) {
        struct can_frame fr;
        ssize_t n = read(s, &fr, sizeof(fr));
        if (n <= 0) break;
        printf("rx id=0x%03X dlc=%d data=", fr.can_id, fr.can_dlc);
        for (int i = 0; i < fr.can_dlc; i++) printf("%02X ", fr.data[i]);
        printf("\n");
    }
    return 0;
}
