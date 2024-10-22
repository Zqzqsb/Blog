---
title: Install Debian On Macbook
createTime: 2024-10-22
author: ZQ
tags:
  - linux
  - 备忘录
permalink: /Linux/OnMacbook/Debian/
---

本文记录在 `Macbook pro 2019`上安装`debian`操作系统的过程。
<!-- more -->

## 前提

本备忘录的前提是将`debian`作为唯一操作系统在`macbook`上使用。不会保留原生的`macos`。

## 装机盘

下载`debian`系统镜像。注意下载完整的镜像，而非网络安装镜像。

使用`diskutil list`识别出装机盘的磁盘标志符。 这一步一定要准确，否则有格式化系统盘的风险。

使用下方的命令将镜像写入磁盘。(假设设备编号为 `disk2`)

```shell
sudo diskutil unmountDisk /dev/disk2  
sudo dd if=path/to/linux.iso of=/dev/disk2 bs=1m
```

## 关闭安全引导

禁用安全启动。 Apple 的安全启动实现在启用时不允许启动除 macOS 或 Windows 之外的任何系统（甚至不允许启动 shim 签名的 GRUB）。我们需要禁用它：

1. 关机
2. 开启并按住 `Command-R` 直到黑屏闪烁，Mac 将在 macOS 恢复模式下启动
3. 从菜单栏中选择“实用程序”>“启动安全实用程序”
4. 进入启动安全实用程序后
5. 将安全启动设置为无安全
6. 将允许启动媒体设置为允许从外部或可移动媒体启动

##  启动安装

1. 关机
2. 插入U盘
3. 按住`option`按键，并且开启，使Mac进入启动引导管理页面
4. 选择EFI的选项，如果有多个就选择最后一个
5. 此时就进入了`debian`安装页面

`debian`的过程和在一般电脑上安装没有差别。

## `T2`安全芯片相关

+ 使用有线适配器链接到网络。
+ 根据该[仓库](https://github.com/AdityaGarg8/t2-ubuntu-repo?tab=readme-ov-file#apt-repository-for-t2-macs)的提示添加源。
+ 现在通过运行以下命令安装 T2 内核和音频配置文件
	+ `sudo apt install linux-t2 apple-t2-audio-config`

现在键盘 触摸板等设备可以正常工作了。

## `WIFI`和蓝牙

> 参考了 `t2-linux` 的五种方法之一

下载一个[脚本](https://wiki.t2linux.org/tools/firmware.sh)，用于从 Apple 下载 macOS 恢复映像。

选择其中的方法5。

## 自定义 `touchbar`

`sudo apt install tiny-dfr`

安装`tiny-dfr`后请确保重新启动Mac。要配置您的 Touch Bar，请运行`sudo touchbar`并按照屏幕上的说明进行操作。

自定义`touchbar`并不稳定。

## 遗留问题

+ 合盖待机后`touchbar` ，`wifi`不能正常工作。
+ `trackpad`默认驱动的手感很差
+ `grone`的键盘映射不习惯
+  系统没有自带的中文输入法

