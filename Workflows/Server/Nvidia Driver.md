---
title: Install Nvidia Driver
createTime: 2024-9-26
author: ZQ
tags:
  - 备忘录
description: 这篇备忘录记录了在linux上安装英伟达显卡驱动的一般过程。
permalink: /server/nvidia/driver/
---
 这篇备忘录记录了在linux上安装英伟达显卡驱动的一般过程。
<!-- more -->

## 下载

对于`Geforce`卡，从[官网](https://www.nvidia.com/en-us/geforce/drivers/)的选择页面根据提示选择相应的驱动版本。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/Driver%20Selection.png)

从驱动列表选择一个，一般来说选择较新的就行。一个大的驱动版本号`535 550 560`会对对应一个`cuda`版本。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/Driver%20Results.png)

复制这个页面的地址，将驱动下载到服务器上，添加执行权限。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/Address.png)

```shell
wget https://us.download.nvidia.com/XFree86/Linux-x86_64/560.31.02/NVIDIA-Linux-x86_64-560.31.02.run
```

```shell
$ ls
data  login.sh  lso_zsh.sh  NVIDIA-Linux-x86_64-560.31.02.run

chmod +x ./NVIDIA-Linux-x86_64-560.31.02.run
```

## 安装

一般来说，执行驱动安装，根据`GUI`的提示安装就可以。下面列出一下可能有问题的地方。

```shell
sudo ./NVIDIA-Linux-x86_64-560.31.02.run --no-x-check
```

### 驱动冲突

根据提示让驱动程序通过修改配置的禁用冲突的驱动。并且选择`rebuild initramfs`。

>是指重建初始RAM文件系统（initramfs）。initramfs 是一个临时的根文件系统，通常在启动时载，它包含了启动操作系统所需的驱动程序和工具。重建 initramfs 通常有以下几种情况。
> +  **内核更新**：当你更新内核或安装新的内核模块时，可能需要重建 initramfs，以确保新的驱动程序和模块被正确加载。
> + **系统配置更改**：如果你更改了与系统启动相关的配置文件（如 `/etc/fstab`），或者安装了新的硬件，重建 initramfs 可以确保这些更改被应用。
> + **修复引导问题**：如果系统在启动时遇到问题，重建 initramfs 可能有助于修复这些问题，确保所有必要的驱动程序和文件都包含在内。
> + **系统迁移或恢复**：在从一个系统迁移到另一个系统或在恢复备份时，可能需要重建 initramfs 以确保兼容性。

完成之后重启系统。

### 协议选择

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/License.png)

选择左边。

### 内核头文件

提示缺少内核头文件

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/KernelHeader.png)

安装内核头文件

```shell
sudo apt-get install linux-headers-$(uname -r)
```

### 更新内核

如果内核版本太久，则拉取不到对应的头文件。更新内核之后**重启系统**，再尝试拉取头文件。

```shell
sudo apt update
sudo apt upgrade // 更新内核
```

```shell
# zhangqing @ debian-24-24 in ~ [16:57:11]
$ uname -r
6.1.0-25-amd64 // 确定内核版本是否更新
```

## 验证

驱动提示安装成功

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Server/NvidiaDriver/Verify.png)
