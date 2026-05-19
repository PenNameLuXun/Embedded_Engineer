# 第 31 章自检题答案

1. (a) 用户指针可能指向被换出 (swap) 的页，普通访问会触发 page fault；(b) 用户和内核可能映射在不同虚拟空间（视架构）；(c) 必须检查指针合法性，避免攻击者传内核地址；(d) 必须支持被中断 / 重试。`copy_to_user/from_user` 处理所有这些，且能正确报告失败。

2. **模块加载失败**。内核打 "hello: probe of ... failed with error -ENNN"，模块不会出现在 `lsmod` 里。所有 init 阶段已分配的资源必须在 return 错误前回滚（典型 goto err_xxx 链）。

3. `MAJOR(dev)` / `MINOR(dev)` 宏。`dev_t` 是 32 位整数：高 12 位 = major（设备类别），低 20 位 = minor（同类内编号）。`MKDEV(major, minor)` 反向构造。

4. **不写编译能过**，但加载时打 `module taints kernel: not enough GPL`，并且模块用到 EXPORT_SYMBOL_GPL 标的内核接口（很多关键接口都标了）会**链接失败**。生产代码遵守开源协议 + 写 LICENSE 是标准做法。
