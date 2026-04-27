---
title: 有了 InnoDB，为什么还需要 MyRocks
createTime: 2026-04-23
author: ZQ
tags:
  - MySQL
  - MyRocks
  - RocksDB
  - InnoDB
permalink: /database/mysql/myrocks/why/
---

> InnoDB 是 MySQL 最成熟的存储引擎，覆盖了绝大多数 OLTP 场景。MyRocks 基于 RocksDB（LSM-tree），在 InnoDB 已经足够好用的前提下仍被 Meta、Percona 等公司引入生产，原因只有一个：**它在特定负载下能用更少的磁盘 I/O 完成同样的工作**。本文从 InnoDB 的结构性开销出发，说明 LSM-tree 如何针对性地缓解这些开销，以及 MyRocks 为此付出的代价。

<!-- more -->

---

## 1. InnoDB 的结构性开销

InnoDB 使用 B+ 树组织数据，这套结构在读多写少、随机点查的场景下非常高效。但它存在几个固有开销，与负载无关，始终存在：

### 1.1 写放大：一次逻辑写触发多次物理写

一次 `UPDATE` 在 InnoDB 内部的写入路径：

```
Undo Log（旧版本，用于回滚和 MVCC）
  ↓
Buffer Pool 脏页（B+ 树节点修改）
  ↓
Redo Log（WAL，顺序写）
  ↓
数据文件（Checkpoint 后异步刷盘，随机 I/O）
```

其中数据文件的刷盘是**随机写**——B+ 树节点分散在磁盘各处，每次修改都可能触发对不同位置的 16KB 页写入。对于写密集型负载，随机 I/O 是 IOPS 的主要消耗来源。

### 1.2 空间放大：页填充率与碎片

InnoDB 按 16KB 固定页管理数据：

- B+ 树插入导致页分裂（page split），新页初始填充率约 50%
- 删除只标记记录为"已删除"，空间不立即回收，需要 `OPTIMIZE TABLE` 重建
- 二级索引与主键索引各自占一棵 B+ 树，存在大量重复的主键列存储

在写入模式为随机 INSERT 或高频 DELETE + INSERT 的场景下，实际磁盘占用往往是数据本身的 2–3 倍。

### 1.3 压缩效果受限

InnoDB 支持页级压缩（`ROW_FORMAT=COMPRESSED`），但：

- 压缩和解压发生在页粒度（16KB），压缩率有限
- 压缩页在 Buffer Pool 中需要同时保留压缩和解压两份拷贝（double write buffer 开销）
- 压缩后页大小不固定，导致磁盘碎片加剧

---

## 2. MyRocks 如何针对性地解决这些问题

MyRocks 将 RocksDB 作为 MySQL 存储引擎接入，核心数据结构从 B+ 树换为 LSM-tree。

### 2.1 顺序写取代随机写

RocksDB 的写路径：

```mermaid
sequenceDiagram
    participant App as 写操作
    participant WAL as WAL（顺序追加）
    participant MT as MemTable（内存跳表）
    participant L0 as L0 SST（Flush）
    participant LN as L1/L2/... SST（Compaction）

    App->>WAL: 顺序追加
    App->>MT: 写入内存
    Note over App: 返回成功
    MT->>L0: MemTable 满后 Flush（顺序写）
    L0->>LN: Compaction（顺序读 + 顺序写）
```

**所有写入都是顺序 I/O**，无论是 WAL、Flush 还是 Compaction。对 SSD 而言，顺序写比随机写更能均匀分布擦写，延长寿命；对 HDD 则能充分利用磁道顺序带宽。

### 2.2 更高的空间利用率

- **无页分裂**：LSM-tree 的 SST 文件是不可变的，写入新版本只追加，不修改旧结构，因此不存在 B+ 树页分裂带来的碎片
- **Compaction 回收空间**：旧版本和删除标记在 Compaction 时被物理清除，磁盘空间自动回收，无需手动 `OPTIMIZE TABLE`
- **前缀压缩**：SST 文件内的 key 按字典序排列，相邻 key 的公共前缀只存一次，显著减少索引存储开销

Meta 的实测数据（2016 年）：将 UDB（用户数据库）从 InnoDB 迁移到 MyRocks 后，同等数据量的磁盘占用下降约 **50%**。

### 2.3 块级压缩更高效

RocksDB 以 block（默认 4KB）为单位压缩，配合 Zstandard（zstd）：

- 压缩率通常比 InnoDB 页级压缩高 20–40%
- 解压只需读取目标 block，不需要加载整页
- SST 文件中压缩块紧密排列，无碎片

---

## 3. MyRocks 付出的代价

LSM-tree 的结构性优势不是免费的，换来写优化的同时引入了新的开销：

| 维度         | InnoDB                   | MyRocks / RocksDB                         |
| ------------ | ------------------------ | ----------------------------------------- |
| 点查性能     | B+ 树一次定位，稳定      | 需查 MemTable + 多层 SST，最坏读放大高    |
| 范围扫描     | 叶子节点链表，顺序读磁盘 | 需合并多层 SST 的迭代器，开销更高         |
| 写放大       | 低至中等（随机写页）     | Compaction 导致数据多次重写，系数 10–30x  |
| 读缓存粒度   | Buffer Pool，页（16KB）  | Block Cache，block（4KB）                 |
| 事务隔离实现 | ReadView + Undo Log 链   | Percolator 协议（TiKV）或 Sequence Number |
| 运维复杂度   | 成熟，工具链完整         | Compaction 调优、空间放大监控额外学习成本 |

### 3.1 读放大

一次点查在最坏情况下需要查：MemTable → L0（多个文件）→ L1 → L2 → …，每层都是一次 I/O。Bloom Filter 可以跳过大多数不含目标 key 的 SST，但对于不存在的 key（negative lookup）仍有概率命中的假阳性开销。

对于**读多写少、随机点查为主**的负载，MyRocks 的读延迟分布通常比 InnoDB 宽，P99 抖动更大。

### 3.2 写放大反转

尽管 RocksDB 的写路径全是顺序 I/O，Compaction 会将一条数据从 L0 一路重写到底层 SST，**写放大系数通常在 10–30 倍**，高于 InnoDB 的随机写页方式。这意味着在极高写入吞吐且 SSD 寿命敏感的场景，需要仔细衡量。

---

## 4. 适合 MyRocks 的负载特征

根据上述分析，MyRocks 相比 InnoDB 有优势的场景集中在：

- **写密集型**：大量随机 INSERT / UPDATE，写 IOPS 成瓶颈
- **磁盘空间敏感**：数据量大、压缩率要求高，如历史数据归档、用户行为日志
- **删除比例高**：频繁 DELETE + 空间回收需求，Compaction 自动处理旧版本
- **主键顺序写入**：如自增主键，LSM-tree 对顺序写入几乎零放大

反之，以下场景仍优先选 InnoDB：

- 读多写少，随机点查为主
- 对读 P99 延迟有严格要求
- 需要成熟的全文索引、空间索引等特性
- 运维团队对 RocksDB 调优经验不足

---

## 5. 常见误读

**"MyRocks 只是 InnoDB 的替代品"**：二者面向不同的负载曲线，不存在全面替代关系。Meta 也只将特定业务（写密集的用户数据库）迁移到 MyRocks，其他业务继续使用 InnoDB。

**"LSM-tree 没有随机写，所以写性能一定更好"**：Compaction 的写放大会消耗后台 I/O 带宽，在 Compaction 高峰期可能影响前台写入延迟，需要合理配置 Compaction 触发策略和带宽限速。

**"MyRocks 的压缩等于 InnoDB 开启压缩"**：InnoDB 的页级压缩与 MyRocks 的块级压缩在粒度、压缩算法、缓存策略上都不同，实际压缩率和 CPU 开销差异显著。
