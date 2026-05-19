# 第 29 章　交叉编译 / Buildroot

> 嵌入式 Linux 系统 = **kernel + bootloader + 根文件系统 (rootfs)**。这三样东西怎么从源码 build 出来？这一章给你两个工具：手工交叉编译（理解每一步），以及 Buildroot（一键 build 全栈）。
>
> **学完本章你应该能**：(1) 解释为什么需要"交叉"编译，(2) 手工用 `arm-linux-gnueabihf-gcc` 编一个 Hello World 并在 QEMU 上跑，(3) 用 Buildroot 5 分钟 build 出能跑的 ARM Linux 镜像，(4) 知道 Buildroot vs Yocto 的差别。

---

## 29.1 为什么要交叉编译

```
开发机 (x86_64)                            目标 (ARM Cortex-A)
   │                                          │
   │ 跑 gcc                                    │ 跑你的程序
   │                                          │
   gcc 默认输出 x86_64 二进制                  ARM 上跑不了
                                              │
   解决：用 ARM 目标的 gcc → arm-linux-gnueabihf-gcc
   它跑在 x86_64 上，但输出 ARM 二进制 → 即"交叉编译"
```

工具链命名约定：`<arch>-<vendor>-<os>-<libc>-gcc`，例：
- `arm-linux-gnueabihf-gcc`：ARM + Linux + glibc + hard-float
- `aarch64-linux-gnu-gcc`：ARM64 + Linux + glibc
- `arm-none-eabi-gcc`：ARM + bare-metal（没 OS，第 2 部分用的）

---

## 29.2 手工：一个 Hello World 跑到 QEMU 上

```bash
# 装工具链 + qemu-user 模式
sudo apt install gcc-arm-linux-gnueabihf qemu-user-static

# Hello.c
cat > hello.c <<'EOF'
#include <stdio.h>
int main(void) { printf("Hello from ARM!\n"); return 0; }
EOF

# 编译
arm-linux-gnueabihf-gcc -static -o hello hello.c
file hello
# → ELF 32-bit LSB executable, ARM, EABI5, statically linked ...

# 跑（qemu-user 模拟 ARM 用户态在 x86_64 上跑）
qemu-arm-static ./hello
# → Hello from ARM!
```

`-static` 让 hello 不依赖目标系统的 glibc，简化第一次实验。**真正项目用动态链接**。

---

## 29.3 直接在 QEMU 跑一个完整 Linux

QEMU 提供 `-machine virt` 这种**纯虚拟**的 ARM 板，零硬件复杂度：

```bash
# 假设你已经 build 好 zImage + virt.dtb + rootfs.cpio.gz
qemu-system-arm -M virt -cpu cortex-a15 -m 512M -nographic \
    -kernel zImage \
    -dtb virt.dtb \
    -initrd rootfs.cpio.gz \
    -append "console=ttyAMA0 init=/bin/sh"
```

输出：

```
Booting Linux on physical CPU 0x0
Linux version 6.x.x ...
...
/bin/sh: can't access tty; job control turned off
# 
```

按 `Ctrl-A x` 退出。

但 zImage / DTB / rootfs.cpio.gz 怎么来？这就是 Buildroot 干的事。

---

## 29.4 Buildroot：5 分钟 build 一个嵌入式 Linux

Buildroot 是一套 Makefile 集合：根据 `.config` 自动下载 + patch + 交叉编译 内核、bootloader、用户程序，最后打包成镜像。

```bash
git clone https://git.buildroot.net/buildroot
cd buildroot

# 用预设的 QEMU ARM 配置
make qemu_arm_vexpress_defconfig

# 进 menuconfig 看看（可选）
make menuconfig

# 开 build —— 第一次约 30 分钟到 2 小时（取决于网速和 CPU）
make

# build 完毕，产物在 output/images/
ls output/images/
# zImage  rootfs.ext2  vexpress-v2p-ca9.dtb  ...
```

跑：

```bash
qemu-system-arm \
    -M vexpress-a9 -smp 1 -m 256 \
    -kernel output/images/zImage \
    -dtb    output/images/vexpress-v2p-ca9.dtb \
    -drive  file=output/images/rootfs.ext2,if=sd,format=raw \
    -append "console=ttyAMA0,115200 root=/dev/mmcblk0 rw" \
    -nographic
```

进 shell 后你能：
```
# uname -a
Linux buildroot 6.x.x ... armv7l GNU/Linux
# ls /
bin  etc  ...
# busybox --list | head
```

**5 分钟之内你拥有了一台完整的虚拟嵌入式设备**。

---

## 29.5 Buildroot 的工作方式

```
buildroot/
├── arch/        ← CPU 架构相关 Makefile
├── board/       ← 板级 defconfig 和补丁
│   ├── qemu/
│   │   ├── arm-vexpress/
│   │   │   ├── post-build.sh
│   │   │   └── readme.txt
│   ├── stm32mp1/
│   ├── raspberrypi/
│   └── ...
├── boot/        ← bootloader 配置 (U-Boot, syslinux, ...)
├── linux/       ← 内核构建逻辑
├── package/     ← 1500+ 用户态包 (busybox, openssh, lighttpd, ...)
│   ├── busybox/
│   │   ├── Config.in     ← Kconfig
│   │   └── busybox.mk    ← Makefile
│   └── ...
├── configs/     ← defconfig 集合
└── output/      ← build 产物
```

加一个新包：写 `package/myapp/Config.in` 和 `package/myapp/myapp.mk`，注册到 `package/Config.in`。Buildroot 自动 download → extract → patch → configure → build → install 到 staging / target。

---

## 29.6 Buildroot vs Yocto

| 维度          | Buildroot                  | Yocto                              |
|---------------|----------------------------|-------------------------------------|
| 哲学          | Makefile + Kconfig，简单   | 元数据 (bb 文件) + Layer，复杂      |
| 学习曲线      | 1 天上手                    | 1 周-1 月                            |
| 增量构建      | 一般                        | 强                                  |
| 输出          | 一个完整镜像                 | 镜像 + SDK + binary packages         |
| 适用规模      | 一两个产品                   | 一个产品族 / 多版本                  |
| 谁在用        | 嵌入式爱好者、中小企业        | 汽车、家电、网络设备大厂              |

Yocto 复杂但工业级；Buildroot 简单但够用 90% 项目。新人先 Buildroot。

---

## 29.7 内核单独 build（不走 Buildroot）

```bash
git clone --depth 1 https://github.com/torvalds/linux
cd linux

# 选个默认配置（ARM virt）
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- multi_v7_defconfig

# 改细节
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig

# Build
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j$(nproc) zImage dtbs modules

ls arch/arm/boot/zImage
ls arch/arm/boot/dts/vexpress-v2p-ca9.dtb
```

约 5–20 分钟。模块安装到目标的方法：`make modules_install INSTALL_MOD_PATH=$TARGET_ROOTFS`。

---

## 29.8 一个最小 rootfs 怎么构造

```
rootfs/
├── bin → busybox-arm
├── sbin → busybox-arm
├── init → busybox-arm
├── etc/
│   ├── inittab
│   └── init.d/
│       └── rcS
├── dev/
├── proc/
├── sys/
└── lib/  (含动态库)
```

打包：
```bash
cd rootfs
find . | cpio -H newc -o | gzip > ../initramfs.cpio.gz
```

`init=/init` + `root=/dev/ram` 启动。这就是教科书级最小 rootfs。

---

## 29.9 自检题

1. `-static` 和动态链接对部署各有什么取舍？
2. Buildroot 重新 build 一个包，要 `make clean` 吗？
3. 内核 `.config` 里 `CONFIG_DEVTMPFS` 关掉，会发生什么？
4. 同一个项目要支持 5 块不同的板子，Buildroot 还是 Yocto 更合适？

答案见 `code/answers.md`。

---

## 29.10 与后续章节的联系

| 概念              | 下游章节                                  |
|-------------------|-------------------------------------------|
| 设备树 (DTB)       | [30 设备树](../30_设备树/)                  |
| 加载驱动模块       | [31 字符设备驱动](../31_字符设备驱动入门/)   |
| Init 脚本          | [28 启动流程](../28_启动流程/) 回顾          |
| OTA 镜像           | [42 OTA](../42_OTA_固件升级/)               |

下一章 [30 设备树](../30_设备树/) 把 DTS 语法学透。
