---
title: Linux 命令 - Rsync
createTime: 2024-8-9
author: ZQ
tags:
  - linux
permalink: /Linux/Command/Rsync/
---

 Rsync命令的使用方式。
 
<!-- more -->

`rsync` 是一个用于同步文件和目录的强大工具，可以在本地和远程系统之间传输数据。它支持显示复制进度，是替代 `cp` 命令的一种有效方式，尤其在你需要监控大文件或大量文件的复制时。它的设计初衷是使文件和目录的备份、镜像、同步等操作变得快速且占用最少的带宽。`rsync` 可以在本地、远程、甚至不同的操作系统之间工作。

## 基本语法

```shell
rsync [选项] 源路径 目标路径
```

## 常见选项

- `-a` (`--archive`): 归档模式，递归复制文件，保留文件的符号链接、权限、时间戳、用户和组信息。
- `-v` (`--verbose`): 显示详细信息。
- `-z` (`--compress`): 在传输时压缩文件，以节省带宽。
- `-h` (`--human-readable`): 使输出更具可读性，使用例如 `K`, `M`, `G` 的格式显示文件大小。
- `--progress`: 显示每个文件的传输进度。
- `--info=progress2`: 显示整体进度，包括总传输速率和剩余时间。

## 常见用法

### 同步本地目录

```shell
rsync -a source/ destination/
```

### 同步本地和远程目录

```shell
rsync -avz source/ user@remote_server:/path/to/destination/
```

### 增量备份

使用 `rsync` 可以执行增量备份，只同步自上次备份以来修改过的文件。

```shell
rsync -a --delete source/ backup/
```

`--delete` 选项会在目标目录中删除源目录中不存在的文件，保持两个目录完全一致。

## 其他

+ `--exclude`: 排除特定的文件或者目录

```shell
rsync -av --exclude='*.tmp' source/ destination/
```

+ `--include`: 仅包含特定的文件或者目录

```shell
rsync -av --exclude='*' --include='*.jpg' source/ destination/
```

仅包含 `.jpg`文件。

+ `--delete`删除目标目录和源目录中不存在人的文件，以使两个目录保持一致:

```shell
rsync -av --delete source/ destination/
```

+ `--dry-run`: 模拟执行，不进行实际的传输

+ `-e` (`--rsh`): 指定远程 shell 程序，通常用于 SSH：

```shell
rsync -av -e ssh source/ user@remote_server:/path/to/destination/
```
