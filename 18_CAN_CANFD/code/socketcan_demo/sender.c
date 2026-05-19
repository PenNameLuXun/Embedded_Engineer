/*
 * SocketCAN 发送演示 - 在 Linux 主机上跑（不需要 QEMU）。
 *
 * 准备虚拟 CAN：
 *   sudo modprobe vcan
 *   sudo ip link add dev vcan0 type vcan
 *   sudo ip link set up vcan0
 *
 * 编译并发送一帧 ID=0x123, data=DEAD BEEF:
 *   make
 *   ./sender vcan0
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
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) {
        perror("SIOCGIFINDEX"); return 1;
    }

    struct sockaddr_can addr = { .can_family = AF_CAN,
                                 .can_ifindex = ifr.ifr_ifindex };
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind"); return 1;
    }

    struct can_frame fr = {
        .can_id  = 0x123,
        .can_dlc = 4,
        .data    = { 0xDE, 0xAD, 0xBE, 0xEF },
    };
    if (write(s, &fr, sizeof(fr)) != sizeof(fr)) {
        perror("write"); return 1;
    }
    printf("sent 0x%03X #DEADBEEF on %s\n", fr.can_id, ifname);
    close(s);
    return 0;
}
