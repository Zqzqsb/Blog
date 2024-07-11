---
title: Linux 文件-特殊权限
createTime: 2024-7-1
author: ZQ
tags:
- linux
description: linux文件特殊权限。
---
<br> linux文件特殊权限。
<!-- more -->

# 概述

在Unix和Linux文件系统中，除了常规的读、写、执行权限外，还有一些特殊权限位(`s`)，可以对文件和目录的行为进行更细粒度的控制。常见的特殊权限包括SUID（Set User ID）、SGID（Set Group ID）和Sticky bit。

# SUID（Set User ID）

- **作用**：当一个可执行文件设置了SUID位后，任何用户执行该文件时，该进程都将以文件所有者的权限运行，而不是以执行用户的权限运行。
- **表示**：在文件权限中，所有者的执行权限位（`x`）会被表示为`s`。
- **设置**：`chmod u+s filename`
- **示例**：`-rwsr-xr-x 1 root root 12345 Jul  1 12:34 /usr/bin/passwd`。示例中，`passwd` 文件的所有者是 `root`，任何用户运行这个程序时，将会以 `root` 的权限执行。

# SGID（Set Group ID）

- **作用**：
    - **文件**：当一个可执行文件设置了SGID位后，任何用户执行该文件时，该进程将以文件所属组的权限运行。
    - **目录**：当一个目录设置了SGID位后，在该目录中新创建的文件或子目录将继承该目录的组，而不是创建者的默认组。
- **表示**：在文件权限中，组的执行权限位（`x`）会被表示为`s`。对于目录，组的执行权限位（`x`）会被表示为`s`。
- **设置**：`chmod g+s filename_or_directory`
- **示例**:  `drwxr-sr-x 2 root staff 4096 Jul 1 12:34 /shared`。上述示例中，`/shared` 目录设置了SGID位，新创建的文件或目录将继承`staff`组。

 # Sticky Bit
 
- **作用**：当一个目录设置了Sticky Bit时，只有文件的所有者、目录的所有者或具有超级用户权限的用户可以删除或移动该目录中的文件。常用于共享目录，如 `/tmp`，以防止用户删除或重命名他人的文件。
- **表示**：在目录的其他用户执行权限位（`x`）会被表示为`t`。
- **设置**：`chmod +t directory`
- **示例**: `drwxrwxrwt 2 root root 4096 Jul  1 12:34 /tmp`。上述示例中，`/tmp` 目录设置了Sticky Bit，其他用户只能删除自己创建的文件。

# 设置和查看特殊权限

- **设置SUID**：`chmod u+s filename`
- **取消SUID**：`chmod u-s filename`
- **设置SGID**：`chmod g+s filename_or_directory`
- **取消SGID**：`chmod g-s filename_or_directory`
- **设置Sticky Bit**：`chmod +t directory`
- **取消Sticky Bit**：`chmod -t directory`
- **查看权限**：`ls -l filename_or_directory`
