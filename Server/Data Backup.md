---
title: Data Backup Solution
createTime: 2024-7-1
author: ZQ
tags:
  - server
  - 备忘录
description: 本文记录自用服务器的数据备份方案。
permalink: /server/backup/
---
 本文记录自用服务器的数据备份方案。
<!-- more -->

## 两地三备份

> ### 是什么

 - **三份备份**：
 	- **原始数据**：数据的主存储，通常是你的工作数据所在的地方。
 	- **本地备份**：第一份备份，存储在与原始数据相同或附近的位置。这份备份提供了快速恢复的能力，适用于小范围的数据丢失或损坏。
 	- **异地备份**：第二份备份，存储在不同的地理位置，通常是远程服务器或云存储。即使发生自然灾害、火灾或其他严重事件导致本地数据全部丢失，这份备份仍然是安全的。
 	
 - **两地存储**：
 	 - **本地存储**：包括原始数据和本地备份。通常是同一个办公室、数据中心或家中。
	 - **异地存储**：地理上远离本地存储的位置，可以是不同的城市、地区甚至国家。

> ### 为什么

- **数据安全**：即使一地的数据完全丢失（例如因自然灾害或盗窃），另一地的备份仍然完好无损。
- **快速恢复**：本地备份提供了快速恢复的能力，减少了恢复时间。
- **灾难恢复**：异地备份确保在极端情况下（如火灾、地震等）仍能恢复数据。
- **分散风险**：降低了单点故障的风险，确保数据的高度可用性和完整性。


##  快照和增量备份

### 快照

#### 特点

1. **瞬时捕捉**：快照是对文件系统在某一特定时间点的一个瞬时捕捉，它反映了文件系统在那个时刻的状态。
2. **存储效率**：快照通常使用写时复制（Copy-on-Write, CoW）技术，写入新数据到原始子卷时，CoW 技术会先将数据块 A 复制到一个新位置 B，然后将新数据写入位置 B。快照仍然指向数据块 A，原始子卷指向数据块 B。因此初始快照不会占用太多存储空间，只有在原始数据发生变化时才会占用空间。
3. **快速创建**：快照的创建和恢复非常快速，因为它们不需要复制大量数据。
4. **本地存储**：快照通常存储在同一个存储卷上，这使得它们对硬盘故障等物理损坏不具备防护能力。

#### 用途

- **快速恢复**：可以快速恢复到快照创建时的状态，适用于快速恢复意外数据更改或删除的情况。
- **测试和开发**：可以在不影响生产数据的情况下测试配置或开发新功能。

### 增量备份

#### 特点

1. **基于变化**：增量备份只备份自上次备份以来发生变化的文件或数据块，因此备份操作和存储空间都更为高效。
2. **备份链**：增量备份通常依赖于先前的全量备份和其他增量备份，因此恢复时需要先恢复全量备份，然后逐步应用各个增量备份。
3. **存储效率**：增量备份相比于全量备份占用更少的存储空间，但恢复时间可能会较长，因为需要逐步应用所有增量备份

#### 用途

- **节省存储空间**：适用于数据变化频繁且存储空间有限的情况。
- **日常备份**：通常作为日常备份策略的一部分，结合定期的全量备份使用。

### 快照 vs 增量备份

|特性|快照|增量备份|
|---|---|---|
|**创建速度**|快速|较快|
|**恢复速度**|快速|较慢，需逐步应用所有增量备份|
|**存储效率**|高效，初始快照占用空间小|高效，仅备份变化数据|
|**存储位置**|通常在本地存储卷|通常在远程或外部存储|
|**保护范围**|对本地文件系统变化提供保护|提供对数据变化的全面保护|
|**适用场景**|快速恢复、测试和开发|日常备份、数据变化频繁的情况|

## btrfs 子卷

+ Btrfs 的快照是基于子卷技术，子卷允许将Btrfs分为几个虚拟文件系统。
+ 创建子卷`sudo btrfs subvolume create /data/sub_volume_name`
+ 注意`/data`必须是一个btrfs文件系统根目录。

## btrbk

+ [github仓库](https://github.com/digint/btrbk)

### 概述

>  **性质：**

1. **btrbk** 是一个专门用于 Btrfs 文件系统的备份工具。
2. **Btrfs** 是一个现代的文件系统，提供了许多高级功能，如快照、子卷和内置的 RAID 支持。
3. **btrbk** 利用 Btrfs 的快照功能进行备份，支持本地和远程备份。

> **功能：**

- **快照备份：** 使用 Btrfs 的快照功能，能够快速创建一致性备份。
- **增量备份：** 通过 Btrfs 的快照和发送/接收功能，实现增量备份。
- **本地和远程备份：** 支持将快照发送到本地或远程的 Btrfs 文件系统。
- **多级备份策略：** 支持多级备份策略，如每日、每周和每月备份。
- **轻量级和高效：** 由于利用了 Btrfs 的内置功能，备份过程非常高效。

### 使用

#### 安装

+ btrbk 是一个纯脚本工具 可以下载 然后丢到 `/usr/bin`下面。

```shell
wget https://raw.githubusercontent.com/digint/btrbk/master/btrbk
chmod +x btrbk
```

+ 测试运行 `sudo ./btrbk ls /` 列出可用的btrfs文件系统(物理卷以及子卷)

```shell
MOUNT_SOURCE    ID   FLAGS  PATH
/dev/nvme1n1p1    5  -      /data
/dev/nvme1n1p1  256  -      /data/DockerAppData
/dev/nvme1n1p1  257  -      /data/TestData
/dev/md0          5  -      /hdd
```

```shell
mv btrbk /usr/bin
```

#### 配置

+ 创建`/etc/btrbk/btrbk.conf`文件
+ 编辑文件(做本地快照)，具体含义如下。

```
# 文件系统内快照的配置
# 时间戳格式
timestamp_format        long
# 快照至少存留的时间
snapshot_preserve_min   18h
# 持久化快照的间隔
snapshot_preserve       48h

# 远端目标位置中的配置(增量备份)
target_preserve_min    no         # 没有最小快照数量限制
target_preserve        20d 10w *m # 日快照保留20天 周快照10周 月快照永久保留


# 快照存储的目录 需要手动创建 并且在同一文件系统内
snapshot_dir /data/.btrbk_snapshots

# 需要备份的目录
volume /data
  target  /hdd/BtrbkSnapshots # target标志另一个文件系统的增量备份位置
  subvolume   /data/TestData
```

#### 创建快照

+ 使用`btrbk run -n -S` 试运行一下，观察一下

```shell
SNAPSHOT SCHEDULE
-----------------
ACTION  SUBVOLUME                                      SCHEME    REASON
create  /data/.btrbk_snapshots/TestData.20240701T2054  18h+ 48h  preserve hourly: first of hour, 0 hours ago

BACKUP SCHEDULE
---------------
ACTION  SUBVOLUME                                   SCHEME                      REASON
create  /hdd/BtrbkSnapshots/TestData.20240701T2054  20d 10w *m (sunday, 00:00)  preserve monthly: first weekly of month 2024-06 (1 months ago, 1d 20h after sunday 00:00)

--------------------------------------------------------------------------------
Backup Summary (btrbk command line client, version 0.33.0-dev)

    Date:   Mon Jul  1 20:54:48 2024
    Config: /etc/btrbk/btrbk.conf
    Dryrun: YES

Legend:
    ===  up-to-date subvolume (source snapshot)
    +++  created subvolume (source snapshot)
    ---  deleted subvolume
    ***  received subvolume (non-incremental)
    >>>  received subvolume (incremental)
--------------------------------------------------------------------------------
/data/TestData
+++ /data/.btrbk_snapshots/TestData.20240701T2054
*** /hdd/BtrbkSnapshots/TestData.20240701T2054

NOTE: Dryrun was active, none of the operations above were actually executed!
```

+ 在试运行log中，snapshot 和 增量备份文件都出现在了对应位置。

#### 恢复实验

+ 首先使用 `btrbk run`创建第一个快照和备份文件。

```shell
--------------------------------------------------------------------------------
Backup Summary (btrbk command line client, version 0.33.0-dev)

    Date:   Tue Jul  2 00:45:54 2024
    Config: /etc/btrbk/btrbk.conf

Legend:
    ===  up-to-date subvolume (source snapshot)
    +++  created subvolume (source snapshot)
    ---  deleted subvolume
    ***  received subvolume (non-incremental)
    >>>  received subvolume (incremental)
--------------------------------------------------------------------------------
/data/TestData
+++ /data/.btrbk_snapshots/TestData.20240702T0045
*** /hdd/BtrbkSnapshots/TestData.20240702T0045
```

+ 删除TestData

```shell
➜  /data rm -rf TestData
➜  /data ls
DockerAppData  DockerAppData.backup  TestData.backup
```

**从快照恢复**

+ 找出可用的子卷。

```shell
➜  /data sudo btrbk list snapshots
SOURCE_SUBVOLUME  SNAPSHOT_SUBVOLUME                             STATUS
/data/TestData    /data/.btrbk_snapshots/TestData.20240702T0045  -
```

+ 删除损坏的卷，或者它已经不见了

```shell
mv /data/TestData /data/TestData.BROKEN
```

+ 从快照恢复

```shell
➜  /data sudo btrfs subvolume snapshot /data/.btrbk_snapshots/TestData.20240702T0045 /data/TestData
Create a snapshot of '/data/.btrbk_snapshots/TestData.20240702T0045' in '/data/TestData'
➜  /data cd TestData
➜  TestData ls
FileBrowser  MariaDB  Memos  NetData  PhotoPrism
```

**从增量备份恢复**

+ 首先将快照删掉

```shell
sudo btrfs subvolume delete /data/.btrbk_snapshots/TestData.20240702T0105
```

+ 将增量备份恢复为快照。
+ 如果有多个增量备份，使用 -p 参数流传到同一个快照。

```shell
➜  BtrbkSnapshots sudo btrfs send ./TestData.20240702T0105 | sudo btrfs receive /data/TestData.snapshot
At subvol ./TestData.20240702T0105
At subvol TestData.20240702T0105
```

+ 接着按照上面从快照恢复的办法即可。

```shell
➜  /data sudo btrfs subvolume snapshot /data/.btrbk_snapshots/TestData.20240702T0105 /data/TestData
Create a snapshot of '/data/.btrbk_snapshots/TestData.20240702T0105' in '/data/TestData'
➜  /data ls
DockerAppData  DockerAppData.backup  TestData  TestData.backup
➜  /data sudo btrbk ls /
MOUNT_SOURCE    ID   FLAGS     PATH
/dev/nvme1n1p1    5  -         /data
/dev/nvme1n1p1  264  readonly  /data/.btrbk_snapshots/TestData.20240702T0105
/dev/nvme1n1p1  256  -         /data/DockerAppData
/dev/nvme1n1p1  265  -         /data/TestData
/dev/md0          5  -         /hdd
/dev/md0        257  readonly  /hdd/BtrbkSnapshots/TestData.20240702T0105
➜  /data ls
DockerAppData  DockerAppData.backup  TestData  TestData.backup
➜  /data cd TestData
➜  TestData ls
FileBrowser  MariaDB  Memos  NetData  PhotoPrism
```

+ 数据也能正常恢复。

## 远端备份

+ 这里的方案比较简单，使用脚本将增量备份目录存储到oss对象存储中。
+ 没有考虑数据加密
+ --update只上传新的文件

```shell
#!/bin/bash

# 配置参数
OSSUTIL_PATH="/usr/bin/ossutil"         # ossutil 的路径
LOCAL_DIR="/hdd/BtrbkSnapshots"         # 本地备份目录
COMPRESSED_DIR="/hdd/CompressedArchives" # 压缩文档的目录
BUCKET_NAME="oss://alicloud-backup"     # OSS 存储桶名称
LOG_FILE="./backup.log"                 # 日志文件路径

# 记录开始时间
echo "Starting backup to OSS at $(date)" >> $LOG_FILE

# 遍历本地备份目录中的所有增量备份文件
for backup_file in "$LOCAL_DIR"/*; do
  # 获取增量备份文件的文件名
  backup_filename=$(basename "$backup_file")
  # 设置对应的压缩文件名（不加时间戳）
  compressed_file="$COMPRESSED_DIR/${backup_filename}.tar.gz"

  # 检查压缩文件是否已经存在
  if [ -f "$compressed_file" ]; then
    echo "Compressed file $compressed_file already exists. Skipping." >> $LOG_FILE
  else
    # 压缩增量备份文件
    tar -zcf "$compressed_file" "$backup_file"
    echo "Compressed $backup_file to $compressed_file." >> $LOG_FILE
  fi
  # 将压缩文件同步到 OSS 存储桶
  $OSSUTIL_PATH cp --update "$compressed_file" $BUCKET_NAME >> $LOG_FILE 2>&1
    # 检查上传是否成功
    if [ $? -eq 0 ]; then
        echo "Uploaded $compressed_file to OSS successfully." >> $LOG_FILE
    else
        echo "Failed to upload $compressed_file to OSS." >> $LOG_FILE
    fi
done

echo "Backup process completed at $(date)" >> $LOG_FILE
```


## 定时任务

+ 编辑crontab 创建两个定时任务

```shell
0 3 * * * /usr/bin/btrbk --config /etc/btrbk/btrbk.conf run
0 4 * * * /home/zq/Scripts/OssBackup/backup_to_oss.sh
```
