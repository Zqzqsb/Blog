---
title: Docker Vitualization
createTime: 2024-11-28
description: 本文记录了docker的基本命令。
tags:
  - docker
author: ZQ
permalink: /docker/vitualization/
---
 本文记录了docker的基本命令。
<!-- more -->

讨论了`docker`的虚拟化和传统虚拟化的差别。

<!-- more -->

## 什么是虚拟化？

**虚拟化** 是一种通过软件创建虚拟版本的技术，包括操作系统、存储设备、网络资源等。它允许在一台物理机器上运行多个独立的虚拟环境，每个环境可以运行不同的操作系统和应用程序。这种技术提高了资源利用率、灵活性和可管理性。

主要的虚拟化类型包括：

- **全虚拟化（Full Virtualization）**：完全模拟硬件环境，允许未修改的操作系统运行。
- **半虚拟化（Paravirtualization）**：操作系统需要修改以适应虚拟化环境。
- **操作系统级虚拟化（OS-Level Virtualization）**：多个隔离的用户空间实例共享同一个操作系统内核。

## 传统虚拟机的工作原理

传统虚拟机通过 **虚拟机监控器（Hypervisor）** 来实现虚拟化。Hypervisor 分为两类：

1. **Type 1 Hypervisor（原生或裸机Hypervisor）**：直接运行在物理硬件之上，如 VMware ESXi、Microsoft Hyper-V。
2. **Type 2 Hypervisor（托管Hypervisor）**：运行在主机操作系统之上，如 VMware Workstation、VirtualBox。

### 主要组成部分

- **虚拟硬件**：包括虚拟CPU、内存、硬盘、网络接口等。
- **虚拟机操作系统**：每个虚拟机都运行一个完整的操作系统实例。
- **管理工具**：用于创建、配置和管理虚拟机。

### 工作流程

1. **资源分配**：Hypervisor 将物理资源分配给各个虚拟机。
2. **隔离**：每个虚拟机相互隔离，运行独立的操作系统和应用。
3. **仿真硬件**：Hypervisor 模拟硬件环境，使得虚拟机无需感知底层物理硬件的差异。

### 优缺点

**优点**：

- 强大的隔离性和安全性。
- 可以运行不同的操作系统。
- 适用于多租户环境。

**缺点**：

- 较高的资源开销，因为每个虚拟机需要运行一个完整的操作系统。
- 启动时间较长，通常在几秒到几分钟之间。

## Docker的虚拟化原理

与传统虚拟机不同，Docker 采用 **操作系统级虚拟化（OS-Level Virtualization）**，通过共享主机操作系统内核，创建多个隔离的用户空间实例（容器）。这种方式使得 Docker 容器更加轻量级和高效。

### Namespace

**Namespace** 是 Linux 内核提供的一种机制，用于为进程创建隔离的环境。它确保每个容器只能看到属于自己的资源，提升了隔离性和安全性。

**常见的 Namespace 类型**

1. **PID Namespace**：隔离进程ID，使得容器内的进程ID从1开始，与主机和其他容器的进程ID独立。
2. **NET Namespace**：隔离网络资源，包括网络接口、路由表、防火墙规则等。
3. **IPC Namespace**：隔离进程间通信资源，如信号量、消息队列等。
4. **MNT Namespace**：隔离挂载点，使得容器可以有自己的文件系统视图。
5. **UTS Namespace**：隔离主机名和域名，使得容器可以有独立的主机标识。
6. **USER Namespace**：隔离用户和用户组，使得容器内的用户映射到主机的不同用户。

**示例**

```bash
# 查看当前进程的 Namespace 信息
lsns
```

### Cgroup

**Cgroup（控制组）** 是 Linux 内核的一项功能，用于限制、控制和监控进程组使用的资源，如CPU、内存、磁盘I/O等。Cgroup 确保每个容器在资源使用上得到合理分配，避免资源争用。

**主要功能**

+ **资源限制**：限制容器使用的CPU、内存等资源。
+ **资源隔离**：确保容器之间的资源使用互不干扰。
+ **资源优先级**：分配不同的资源优先级，确保关键容器获得足够资源。

**示例**

```bash
# 查看某个Cgroup的内存限制
cat /sys/fs/cgroup/memory/docker/<container-id>/memory.limit_in_bytes
```

### 联合文件系统（Union File System）

**联合文件系统（Union File System）** 是 Docker 镜像层的基础，允许多个文件系统层叠加，形成一个统一的文件系统视图。这使得 Docker 镜像具有轻量级和可复用性的特点。

**常见的联合文件系统**

+ **AUFS（Advanced Multi-Layered Unification Filesystem）**
+ **OverlayFS**
+ **Btrfs**
+ **ZFS**

**工作原理**

1. **镜像层**：每个镜像由多个只读层组成。
2. **容器层**：在镜像之上添加一个可写层，记录容器的变化。
3. **联合挂载**：多个层叠加在一起，形成一个统一的文件系统视图。

**优势**

+ **节省空间**：相同的文件可以在多个镜像中共享。
+ **快速部署**：通过层叠机制，加快镜像的构建和部署速度。
