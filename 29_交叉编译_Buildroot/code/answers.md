# 第 29 章自检题答案

1. **静态**：把所有依赖打进单个二进制，部署简单（拷过去就跑），目标 rootfs 可以极简。**动态**：二进制小、节省 RAM（多个程序共享同一份 libc）、便于升级 libc 修补漏洞。嵌入式生产：用动态、共享 libc；调试 / busybox / 最小 rescue 镜像：静态。

2. 不需要 `make clean` 全清。Buildroot 用 `make pkgname-rebuild` 只重建那一个包。`make pkgname-dirclean` 删该包的 build 目录后重做。**用 `make clean` 会丢掉所有缓存，重 build 几小时**。

3. 没有 devtmpfs，**`/dev` 目录没人自动填**节点。busybox 系统里你得手工 `mknod` 或加 mdev。新内核默认开 devtmpfs 是为了傻瓜化，关掉是高级用户的优化（嵌入式 ROM 极紧时省几 KB）。

4. **Yocto**。多板共享一个 Layer 体系：通用 Layer + 每个板 Layer + 应用 Layer，扩展性比 Buildroot 强一个量级。Buildroot 多板要复制 defconfig 维护，发散快。Yocto 学习曲线陡但对多产品线值。
