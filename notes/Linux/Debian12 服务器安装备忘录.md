---
title: Debian12 服务器安装备忘录
createTime: 2024-5-27
author: ZQ
tags:
  - linux
  - 备忘录
description: 本文记录debian12作为服务器的安装和配置过程
permalink: /debian_server/
---
<br> 本文记录debian12作为服务器的安装和配置过程
<!-- more -->

## 前言

本文记录自用的debian服务器的安装和配置过程。服务器的硬件配置如下。

| 类别           | 型号                  |
| ------------ | ------------------- |
| CPU          | 12700k              |
| Mother Board | z690                |
| DRAM         | DDR4 16G * 2        |
| System Drive | 970EVO 512G PCIE3.0 |
| Data Drive   | Gloway 4TB PCIE4.0  |
| BackUp Drive | 日立 10TB * 2         |
| CASE         | 半岛铁盒 F20            |
| Power Supply | 利民TG1000 1000w      |

## 熟悉命令

### `fdisk`

> `fdisk` 是 Linux 系统上一个常用的磁盘分区工具。它可以用来查看、创建、删除和修改磁盘分区。该命令需要在sudo权限下执行。

1. 列出磁盘分区信息 `sudo fdisk -l`
2. 进入交互式分区编辑模式 为特定设备分区 `sudo fdisk [dev/device_name]`

### `parted`

> `parted` 是 Linux 系统上一个功能强大且更加用户友好的磁盘分区工具,它是对传统 `fdisk` 命令的一种补充和升级。与 `fdisk` 相比,`parted` 具有以下一些优势:

1. **支持更大磁盘**: `parted` 可以处理超过 2TB 的大容量磁盘,而 `fdisk` 对磁盘容量有一定限制。
2. **支持更多文件系统**: `parted` 支持常见的文件系统类型,如 `ext4`、`btrfs`、`XFS` 等,而 `fdisk` 只能识别基本的 DOS 分区表。
3. **更友好的交互界面**: `parted` 提供了更加人性化的交互界面,使用起来更加直观和方便。
4. **支持动态调整分区**: `parted` 支持在不重启系统的情况下动态调整磁盘分区的大小和位置。这在扩容或重新规划磁盘时非常有用。
5. **更好的错误处理**: `parted` 会在执行危险操作时提示用户确认,并会尽量避免造成数据丢失。

该命令的使用方式和fdisk类似

1. 列出磁盘分区信息 `sudo parted -l`
2. 进入交互式分区编辑模式 为特定设备分区 `sudo parted [dev/device_name]`

### `mdadm`

>`mdadm` 是 Linux 系统上用于管理软件 RAID 的一个强大工具。它允许用户创建、监控和管理各种类型的 RAID 阵列,包括 RAID 0、RAID 1、RAID 5、RAID 6 等。

1. 创建RAID阵列,例子为一个RAID5阵列 包四个块设备 阵列会表现为一个统一的块设备md0

```shell
sudo mdadm --create /dev/md0 --level=5 --raid-devices=4 /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1
```

2. 查看RAID阵列状态

```shell
sudo mdadm --detail /dev/md0
```

3. 扩展RAID阵列，RAID5，RAID6支持热扩展

```shell
sudo mdadm --grow /dev/md0 --raid-devices=5
```

4. 从RAID阵列中移出设备

```shell
sudo mdadm --remove /dev/md0 /dev/sde1
```

5. 添加热备份设备，热备设备是应对整列故障的预备块设备，会自动替换故障设备

```shell
sudo mdadm --add /dev/md0 /dev/sdf1
```

6. 定期监控RAID阵列,并发送邮件

```shell
sudo mdadm --monitor --scan --mail=your@email.com
```

7. 重新组装一个之前创建的RAID阵列

```shell
sudo mdadm --assemble /dev/md0 /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1
```

### `lsblk`

> `lsblk` 是 Linux 系统上一个非常有用的块设备列表查看命令。它能快速、直观地显示系统中所有块设备的拓扑结构和属性信息。

```shell
➜  ~ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
sda           8:0    0   9.1T  0 disk
└─sda1        8:1    0   9.1T  0 part
  └─md0       9:0    0   9.1T  0 raid1 /hdd
sdb           8:16   0   9.1T  0 disk
└─sdb1        8:17   0   9.1T  0 part
  └─md0       9:0    0   9.1T  0 raid1 /hdd
nvme1n1     259:0    0 465.8G  0 disk
├─nvme1n1p1 259:1    0   512M  0 part  /boot/efi
├─nvme1n1p2 259:2    0 464.3G  0 part  /
└─nvme1n1p3 259:3    0   976M  0 part  [SWAP]
nvme0n1     259:4    0   3.7T  0 disk
└─nvme0n1p1 259:5    0   3.7T  0 part  /data
```

### `mkfs`

>`mkfs`命令是Linux和Unix系统中用于创建文件系统的命令。它的全称是"make file system"。

1. **基本用法**:
    - `mkfs [options] device`：在指定设备上创建文件系统。
2. **常用选项**:
    - `-t`：指定要创建的文件系统类型,如ext4、xfs、btrfs等。
    - `-b`：指定文件系统块大小。
    - `-i`：指定每个inode的字节数。
    - `-L`：指定文件系统卷标。
    - `-m`：指定保留给root用户的空间百分比。
    - `-c`：在创建文件系统前检查设备是否有坏块。
3. **创建不同类型的文件系统**:
    - `mkfs -t ext4 /dev/sdb1`：创建ext4文件系统。
    - `mkfs -t xfs /dev/sdc1`：创建XFS文件系统。
    - `mkfs -t btrfs /dev/sdd1`：创建btrfs文件系统。
4. **注意事项**:
    - 执行`mkfs`命令会彻底格式化指定设备,将现有数据全部删除,请谨慎操作。
    - 不同的文件系统有不同的特点和适用场景,请根据实际需求选择合适的文件系统类型。
    - 文件系统创建完成后,还需要将其挂载到相应的挂载点才能使用。

### `mount`

> `mount`命令用于在Linux系统中挂载文件系统。

1. **基本语法**:
    - `mount [-t type] [-o options] device directory`
2. **常用选项**:
    - `-t type`: 指定要挂载的文件系统类型,如ext4、xfs、nfs等。
    - `-o options`: 指定挂载选项,如ro(只读)、rw(读写)、async(异步)等。多个选项用逗号分隔。
    - `-a`: 挂载/etc/fstab中列出的所有文件系统。
    - `-L label`: 通过文件系统卷标挂载。
    - `-U uuid`: 通过文件系统UUID挂载。
3. **挂载示例**:
    - `mount /dev/sdb1 /mnt`: 将/dev/sdb1设备挂载到/mnt目录。
    - `mount -t ext4 /dev/sdc1 /data`: 将ext4文件系统/dev/sdc1挂载到/data目录。
    - `mount -t nfs 192.168.1.100:/share /mnt/nfs`: 将NFS共享目录挂载到/mnt/nfs。
    - `mount -o ro /dev/sdb1 /media`: 以只读方式挂载/dev/sdb1到/media目录。
### `df`

>`df`命令是Linux和Unix系统中用于显示文件系统磁盘空间使用情况的常用命令。

1. **基本用法**:
    - `df`：显示所有已挂载文件系统的磁盘使用情况。
2. **选项**:
    - `-h`：以人类可读的方式显示磁盘空间大小,如MB、GB等。
    - `-i`：显示inode使用情况而不是磁盘空间。
    - `-T`：显示文件系统类型。
    - `-t`：只显示指定类型的文件系统。
    - `-x`：排除指定类型的文件系统。
3. **指定文件系统或路径**:
    - `df /home`：只显示包含/home目录的文件系统。
    - `df /dev/sda1`：显示指定设备的文件系统信息。
4. **其他用法**:
    - `df -h`：以人类可读的格式显示磁盘使用情况。
    - `df -i`：显示文件系统inode使用情况。
    - `df -Th`：显示文件系统类型和人类可读的磁盘空间信息。
    - `df -x tmpfs`：排除tmpfs类型的文件系统。
5. **输出解释**:
    - **Filesystem**：文件系统名称或设备名称。
    - **1K-blocks**：总磁盘容量,单位为1KB块。
    - **Used**：已使用容量。
    - **Available**：可用容量。
    - **Use%**：已使用容量的百分比。
    - **Mounted on**：文件系统挂载点。

### `du`

> `du`命令是Linux系统中用于估计文件或目录占用磁盘空间大小的工具。

1. **查看目录或文件占用空间**
    - `du path`: 显示指定目录或文件的磁盘使用情况。
    - `du -h path`: 以人类可读的格式(KB、MB、GB等)显示磁盘使用情况。
2. **递归统计目录大小**
    - `du -s path`: 只显示指定目录的总使用空间,不显示子目录。
    - `du -a path`: 显示指定目录及其所有子目录和文件的使用空间。
    - `du -d n path`: 仅显示嵌套层数不超过n层的目录使用情况。
3. **排序输出结果**
    - `du -h | sort -h`: 按照人类可读的格式对结果进行排序。
    - `du | sort -n`: 按照字节数大小对结果进行排序。
4. **排除特定目录或文件**
    - `du --exclude=pattern path`: 排除匹配指定模式的文件或目录。
    - `du --max-depth=n path`: 仅统计指定目录及其n层子目录。
5. **总结磁盘使用情况**
    - `du -c`: 在输出结果的最后显示总的磁盘使用量。
    - `du -s /`: 显示整个根目录的磁盘使用情况。
6. **结合管道使用**
    - `du path | sort -n | head -n 5`: 列出指定目录下占用空间最大的前5个子目录。
    - `du -ak / | sort -n | tail -n 1`: 显示根目录下占用空间最大的单个文件或目录的大小。

## 相关知识

### `UUID`

> UUID（Universally Unique Identifier）是一种标识符,用于在分布式计算环境中唯一地标识信息。它的主要特点包括:

1. **唯一性**：UUID被设计成在全球范围内是唯一的。通过使用足够长的标识符(128位)以及随机和伪随机数生成算法,可以确保不会出现重复的UUID。
2. **分散性**：UUID不需要集中的注册机构即可生成。任何个体或组织都可以独立地生成自己的UUID,而不会与他人的UUID冲突。
3. **可读性差**：UUID由32个16进制字符组成,通常以连字符分隔成8-4-4-4-12的格式显示,例如"550e8400-e29b-41d4-a716-446655440000"。这种形式不太便于人工识别和记忆。
4. **应用广泛**：UUID广泛应用于计算机软件中,尤其是在分布式系统、数据库、文件系统等领域,用于标识各种对象,如文件、设备、用户帐户等。

当你在一个存储设备上创建一个新的分区并格式化为某种文件系统（例如ext4、xfs等）的时候，文件系统会自动生成一个UUID。这个UUID是在文件系统创建的过程中随机生成的，因此即使你在相同的设备上创建相同大小、相同类型的文件系统，它们的UUID也会不同。

UUID的主要作用是提供一个在全局范围内唯一的标识符，用于唯一地标识一个特定的文件系统，这样即使存储设备的设备名（例如/dev/sda1、/dev/sdb2等）改变，系统也能通过UUID找到正确的设备。

### `fstab`

`/etc/fstab`用于实现系统启动时的自动挂载。

```shell
<设备>    <挂载点>    <文件系统类型>     <挂载参数>    <转储频率>    <自检顺序>
/dev/sda1  /          ext4            defaults    0            1
/dev/sda2  /home      ext4            defaults    0            2
/dev/md0   /data      xfs             defaults    0            0
192.168.1.100:/share  /mnt/nfs  nfs   defaults    0            0
```

> 其中各字段的含义如下:

1. `<设备>`: 这可以是设备名、UUID（通用唯一识别码）、LABEL（标签）或者PARTUUID（分区的UUID）。
2. `<挂载点>`: 要挂载到的目录,必须事先创建好。
3. `<文件系统类型>`: 如ext4、xfs、nfs等。
4. `<挂载参数>`: 挂载时使用的可选参数,如`defaults`、`noatime`、`rw`等。
5. `<转储频率>`: 0表示不备份,1表示每天备份,2表示隔天备份。
6. `<自检顺序>`: 0表示不自检,1表示第一个自检,2表示第二个自检,以此类推。

要实现自动挂载,只需在`/etc/fstab`中添加相应的条目即可。挂载点必须事先创建好,文件系统类型和挂载参数要根据实际情况设置。

修改`/etc/fstab`文件后,可以使用`mount -a`命令立即生效,或者重新启动系统让配置生效。

### `btrfs`

>btrfs是一种新型的Linux文件系统,它提供了许多先进的功能和特性,包括:

1. **写时复制(COW)**: btrfs采用写时复制机制,可以快速创建快照和副本,而不占用额外的磁盘空间。这对备份和数据恢复很有帮助。
2. **子卷和快照**: btrfs支持创建子卷,可以作为独立的文件系统进行管理。快照功能可以快速记录子卷的状态。
3. **RAID支持**: btrfs内置RAID功能,可以实现数据的冗余和容错。支持多设备RAID0、RAID1、RAID10等模式。
4. **压缩**: btrfs支持透明的在线压缩,可以降低存储空间的使用。
5. **自动碎片整理**: btrfs具有自动碎片整理功能,可以最小化磁盘碎片。
6. **校验和**: btrfs会对数据和元数据计算校验和,可以发现并修复数据损坏。
7. **在线扩容和缩容**: btrfs支持在线扩容和缩容,可以动态调整文件系统大小。
8. **事务性操作**: btrfs支持事务性操作,可以确保元数据的一致性。

随着时间的推移,它也必将成为更多Linux发行版的默认选择。

- 在Debian中,btrfs-tools软件包提供了管理btrfs文件系统的命令行工具。
- 可以使用以下命令安装:

```shell
sudo apt-get install btrfs-tools
```


##  Pipeline

### 1. 材料准备

+  存储`debian12` 系统iso的u盘

### 2. 修改`UEFI`启动

+ 进入`BIOS`并修改启动方式，将装机盘设置位启动首选项
+ 对于民用级主板，一般为`F11` , `F12` 或者 `Del`
+ 对于DELL服务器进入`BIOS`的触发键位`F2`

### 3. 插入装机盘 安装系统

+ 使用非图形化界面
+ 安装 `ssh server`不需要安装GUI
+ 安装过程不需要进行网络配置
+ 安装过程中会创建一个新的常规用户
	+ 如果操作的是NISL Server `root`的密码是<p style="filter: blur(10px);">cannot tell you 😈</p>
	+ 如果操作的是NISL Server新用户名为 `installer` 密码为<p style="filter: blur(10px);">  cannot tell you 😈 </p>
+ 系统安装在970 EVO中，自动分区，其他磁盘均为未挂载状态。
### 4. 配置基本网络

#### 4.1 网络配置

调整网络配置 `/etc/network/interfaces`，使得其形如

```c
auto enp6s0f0
iface enp6s0f0 inet static
    address 10.176.25.53
    netmask 255.255.254.0
    gateway 10.176.24.1
```

- `address` 是静态地址，需要按照不同机器进行分配
- `netmask` 是子网掩码，为 `23` 位，该长度固定。
- `gateway` 是网关，可由子网掩码计算得出，固定。

重启网络服务

```shell
sudo systemctl restart networking.service
```

#### 4.2 校园网认证

+ 挂载U盘
+ 将U盘的登录脚本拷贝
+ 使用登录脚本登录

### 5. 配置SSH

#### 5.1 禁用密码登录

修改 `/etc/ssh/sshd_config`

```shell
#line 57:
PasswordAuthentication no
```

#### 5.2 生成秘钥

> 如果是操作 NISL Server 则为 `installer`用户生成秘钥

- 生成秘钥

```sh
# 生成秘钥
ssh-keygen -t rsa -b 4096
```

- 将公钥改名为 `authorized_keys`

```sh
cd ./.ssh
cat id_rsa.pub >> authorized_keys
rm id_rsa.pub
```

- 将私钥拷贝到 U 盘（临时挂载点）上面

```sh
cp ./id_rsa ../install_tmp
```

+ **在这一步完成后，可以离开实体机，进行远程操作。**

### 6. 修改DNS服务器

- 修改配置文件

```bash
vi /etc/resolv.conf
```

- 添加如下内容

```sh
# 在原始文件基础上添加
nameserver 202.120.224.26
nameserver 114.114.114.114
nameserver 8.8.8.8
```

- 重新加载配置文件

```sh
/etc/init.d/networking restart
```

### 7.  apt 换源

+ 将 `/etc/apt/sources.list`中的内容整体替换为

```sh
# 统一采用阿里云镜像 
deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib deb-src https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib deb https://mirrors.aliyun.com/debian-security/ bookworm-security main deb-src https://mirrors.aliyun.com/debian-security/ bookworm-security main deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib deb-src https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib deb https://mirrors.aliyun.com/debian/ bookworm-backports main non-free non-free-firmware contrib deb-src https://mirrors.aliyun.com/debian/ bookworm-backports main non-free non-free-firmware contrib
```
+ 执行升级命令

```sh
#root 
apt-get update && apt-get upgrade 
# 安装必要软件 
apt-get install tmux zsh vim neofetch git sudo curl rsync duf zip unzip screen fzf fd-find
```

### 8. 配置`sudo`

+ 将编辑器从`nano`改为`vim`

```sh
update-alternatives --config editor
```

+ 编辑`visudo`

### 9. 设置时钟同步

- 硬件时钟矫正 `hwclock`
- 设置时间 `date` 和 `hwclock` 同步

```sh
sudo hwclock --systohc
```

+ 修改时间为24时计时法

```sh
sudo vim /etc/default/locale
```

添加

```shell
LANG=en_US.UTF-8
LC_TIME=en_US.UTF-8
```

重新加载守护进程

```sh
sudo systemctl daemon-reload 
# 按照 /etc/fstab 重新挂载 
mount -a
```

### 10. 挂载额外的磁盘

#### data

+ 使用`parted`为块设备`nvme0n1`分区 将整个磁盘分为一个主分区
	+ 将得到分区`nvme0n1p1`
+ 使用`mkfs`将`btrfs`挂载到`nvme0n1p1`

```shell
sudo mkfs.btrfs /dev/nvme0n1p1
```

+ 将`nvme0n1p1`挂载到`/data`挂载点

```shell
sudo mount /dev/nvme0n1p1 /data
```

#### hdd

`/hdd`是一个RAID0阵列，用于进行系统备份。

+ 使用`parted`为块设备`sda`和`sdb`分区 将整个磁盘分为一个主分区
	+ 将得到分区`sda1`和`sdb1`
+ 使用`mdadm`创建一个RAID0阵列 

```shell
sudo mdadm --create --verbose /dev/md0 --level=1 --raid-devices=2 /dev/sda1 /dev/sdb1

```

+ 为`md0`指定一个文件系统

```shell
sudo mkfs.btrfs /dev/md0
```

+ 将此配置写入`/etc/mdadm/mdadm.conf`

```shell
# This configuration was auto-generated on Thu, 23 May 2024 17:54:37 +0800 by mkconf
ARRAY /dev/md0 metadata=1.2 name=nisl-superman:0 UUID=8b0e391f:f36291d9:5acabf5b:8a3fc6d6
```

+ 挂载`md0`到`/hdd`

```shell
sudo mount /dev/md0 /hdd
```

#### 修改 `fstab`

修改后的`fstab`

```shell
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
# / was on /dev/nvme1n1p2 during installation
UUID=fb944645-2483-4472-9f6f-0e50f2115044 /               ext4    errors=remount-ro 0       1
# /boot/efi was on /dev/nvme1n1p1 during installation
UUID=6B59-4865  /boot/efi       vfat    umask=0077      0       1
# swap was on /dev/nvme1n1p3 during installation
UUID=08282ecc-b789-40a2-9d03-c235acc8cf2a none            swap    sw              0       0
# /data was on /dev/nvme0n1p1
UUID=b70bda07-3de3-4dce-9506-d4329d5a8697 /data          btrfs    defaults 0       1
# /hdd was on /dev/md0
UUID=07c21af2-8b30-4121-a78f-c06ebdaefb35 /hdd          btrfs    defaults 0       1
```

## 写在最后

至此，网络连通性和硬件层面的设置都已经完成。可以开始畅玩了🍺🍺🍺。
