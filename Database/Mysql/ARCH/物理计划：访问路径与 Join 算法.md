---
title: 传统查询优化器（四）：物理计划——访问路径与 Join 算法
createTime: 2026-07-22
author: ZQ
tags:
  - Database
  - MySQL
  - 查询优化
  - Nested Loop Join
  - Hash Join
  - 系列
permalink: /database/mysql/physical-plan-access-path-and-join/
---

> **物理计划**把逻辑算子落实成可执行的算法节点：`Scan` 变成全表或某条索引路径，`Join` 变成 Nested Loop / Hash / Sort-Merge 等。本篇把两件最贵的决策拆开讲——**单表怎么读进来**，以及 **Join 时两股数据流如何对齐**——并用逐步示意说明 Nested Loop Join（NLJ）到底在循环什么。

<!-- more -->

**系列导航**：[一·全景](/database/mysql/traditional-query-optimizer/) · [二·逻辑计划](/database/mysql/from-sql-to-logical-plan/) · [三·谓词与改写](/database/mysql/predicate-and-rule-rewrite/) · **四·物理与 Join（本篇）** · [五·代价与搜索](/database/mysql/cost-model-and-plan-search/)

---

## 1. 逻辑节点 → 物理节点

> 同一逻辑算子对应一族物理实现；优化器枚举合法实现，再用代价挑选（代价见[第五篇](/database/mysql/cost-model-and-plan-search/)）。

| 逻辑 | 可能的物理落实 |
|---|---|
| `Scan(R)` + 谓词 | `TableScan` / `IndexRangeScan` / `IndexLookup` / `IndexOnlyScan` |
| `Join(cond)` | `NestedLoopJoin` / `BlockNestedLoop` / `HashJoin` / `SortMergeJoin` |
| `Aggregate` | 流式聚合（输入已序）/ 哈希聚合 |
| `Sort` | 内存排序 / 外部排序 |

物理节点上会挂上：**用哪个索引、驱动表是谁、是否回表、估计行数** 等——这正是 `EXPLAIN` 里那些字段的来源。

---

## 2. 单表访问路径

> **Access path（访问路径）** 在优化器术语里通常很窄：只回答**一张表**的行从存储里**按什么方式读出来**（全表 / 哪条索引 / 是否回表），不是「逻辑计划 → 物理计划」的全部候选。后者叫计划搜索空间：访问路径 × Join 顺序 × Join 算法 …；选型标准是**估计代价最低**，不是步骤更少或树更矮。

访问路径回答：满足谓词的行，从存储里**按什么顺序、读哪些页**取出来。

设表 `users(id PK, country, name, age)`，有二级索引 `idx_age(age)`，查询：

```sql
SELECT name FROM users WHERE age > 18;
```

### 2.1 三条典型候选

```text
A. TableScan
   沿主键/聚簇索引读完表 → 逐行判断 age > 18 → 取 name

B. IndexRangeScan(idx_age) + 回表
   在 idx_age 上定位 age > 18 的键 → 得到主键 → 回聚簇索引取 name

C. IndexOnlyScan（若存在覆盖索引 (age, name)）
   只读二级索引叶子即可拿到 name，无需回表
```

| 路径 | 因为 | 代价直觉 |
|---|---|---|
| 全表 | 无合适索引，或估出来回表更贵 | I/O 随表大小线性涨；过滤在 CPU |
| 二级索引 + 回表 | 谓词能切出较小范围 | 索引顺序读 + 回表随机读；范围很大时可能输给全表 |
| 覆盖索引 | 查询列都在索引里 | 通常最省；索引更宽、写放大更大 |

**回表**：二级索引叶子一般只存「索引键 + 主键」（InnoDB）。要拿 `name` 这种未包含列，必须再用主键去聚簇索引读完整行。回表次数≈命中索引的行数；行多且分散时，随机 I/O 会吞掉「看起来 rows 更少」的优势。

**ICP（Index Condition Pushdown）**：部分本可在 Server 判断的索引条件，下推到引擎在索引层过滤，减少回表次数。这是物理/引擎能力，优化器需要把「能否 ICP」算进候选代价。

---

## 3. Nested Loop Join：嵌套循环在干什么

> NLJ 的本质是两层循环：**外表每一行，到内表去找匹配行**。有可用索引时，内层从「扫表」变成「按键查找」，称为 Index Nested Loop Join。

### 3.1 伪代码

```text
for each row r in Outer:          -- 驱动表 / 外表
    for each row s in Inner
         where join_cond(r, s):   -- 被驱动表 / 内表
        emit (r, s)
```

没有索引时，内层是对内表的扫描（或块化后的扫描）；有索引时：

```text
for each row r in Outer:
    lookup Inner by index using r.join_key
    for each matching s:
        emit (r, s)
```

两层 `for` 还在，但**内层工作量变了**，不能仍按 \(O(n^2)\) 一概而论：

| | 内层每次做什么 | 粗量级（\(N=\|Outer\|\)，\(M=\|Inner\|\)） |
|---|---|---|
| **无索引 NLJ** | 扫完（或块扫）内表再比条件 | 约 \(O(N \times M)\) 次行比较 → 两表同阶时像 \(O(n^2)\) |
| **Index NLJ** | B+ 树按键查找，只碰匹配行 | 约 \(O(N \times (\log M + K))\)，\(K\) 为该次命中行数 |

等值点查、每个外表键只命中常数行（如主键 / 唯一键，或平均匹配很少）时，主导项是 \(N \log M\)，**不是** \(N \times M\)。  
索引没有把「嵌套循环」变成别的控制流，但把内层从线性扫描收成了对数探路 + 沿匹配链吐行。

仍可能显得「像平方」的两种情况，宜分开看：

1. **探测成本**：无合适索引，或每次 lookup 退化成大范围扫 → 又接近 \(N \times M\)。
2. **结果本身很大**：每个外表行命中很多内表行，输出元组数就是 \(\sum K_i\)；最坏可到 \(N \times M\)。那是**结果基数**的代价，换 Hash Join 也要付产出/物化成本，不是「有索引却白做了 \(n^2\) 次全表扫描」。

代价模型写的也是同一句话：`Cost ≈ Cost(Outer) + Card(Outer) × Cost(一次 Inner 探测)`——有索引时「一次探测」≈ 树高 + 回表，而不是整表 \(M\)。

### 3.2 逐步例子

```sql
SELECT o.id, u.name
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.country = 'CN';
```

假设优化器选定：**users 为驱动表**（先滤出 CN 用户），orders 走 `user_id` 索引：

```text
NestedLoopJoin (o.user_id = u.id)
  ├── Outer: IndexRangeScan / Filter (users, country='CN')
  └── Inner: IndexLookup (orders, user_id = u.id)
```

逐步：

```text
1. 从 users 取出第 1 个 CN 用户  u=(id=5, name=Alice)
2. 用 5 去 orders.user_id 索引查找 → 得到订单 101, 108
3. 输出 (101, Alice), (108, Alice)
4. 从 users 取出第 2 个 CN 用户  u=(id=9, name=Bob)
5. 用 9 去查找 → 得到订单 200
6. 输出 (200, Bob)
…直到 users 侧耗尽
```

![3.2 逐步例子](./物理计划：访问路径与%20Join%20算法.assets/3.2-逐步例子.svg)

要点：

- **谁当 Outer 极重要**：Outer 行数 × 单次 Inner 探测成本 ≈ NLJ 主代价。Outer 很大且 Inner 无索引时，容易爆炸。
- **Index Nested Loop**：Inner 探测是点查/小范围扫描，NLJ 才常成为 OLTP 优解。
- **Block Nested Loop**：把 Outer 多行攒成块，减少反复扫 Inner 的次数（无索引 Join 时的缓解手段，不是换算法族）。

### 3.3 和「逻辑 Join」的差别

逻辑计划里的 `Join` 只声明「两表按条件组合」。  
NLJ 额外固定了：

1. 驱动顺序（左/右谁在外层循环）；
2. 内层是扫表还是索引查找；
3. 每行何时做残留 Filter（如 `amount > 100` 在 Lookup 之后）。

同一逻辑 Join，驱动顺序对调就是另一个物理候选，代价可以差几个数量级。

---

## 4. Hash Join：先建桶，再探测

> 等值 Join 时，Hash Join 把一侧（Build）装进哈希表，另一侧（Probe）逐行探测。它不依赖 Inner 上有索引，但依赖内存（或溢写）。

```text
# Build 阶段
表小侧 S 的每行 → 按 join key 哈希，插入哈希表

# Probe 阶段
表大侧 R 的每行 → 算哈希 → 在桶里找匹配 → 输出
```

适用直觉：

- 等值条件（`=`）；非等值通常另议。
- Build 侧过滤后不大，能放进内存（或可接受溢写）。
- Inner **没有**合适索引、NLJ 会沦为反复全表时，Hash Join 常胜出。

和 NLJ 对比：

| | Nested Loop（含 Index NLJ） | Hash Join |
|---|---|---|
| 典型条件 | 任意，索引等值最强 | 主要是等值 |
| 是否需要索引 | Index NLJ 需要 | 不需要 |
| 对驱动侧行数 | 很敏感 | Build 大小敏感 |
| 内存 | 较低（索引探测） | 需要建表内存 |
| MySQL | 长期主力 | 8.0.18+ 引入后进入候选 |

优化器侧含义：引入 Hash Join 后，**候选集合变大**，代价模型必须能给「建表 + 探测 + 溢写」打分，否则新算法形同虚设。

---

## 5. Sort-Merge Join：先有序，再归并

> 两输入若已按 Join 键排序（或愿意付排序成本），可像归并有序链表一样对齐匹配。

```text
将 R、S 分别按 join key 排序（若尚未有序）
i, j 指向两序列头部
while 两边都未结束:
    if R[i].key == S[j].key: 输出所有相等键组合，推进
    else 推进较小键一侧
```

适用直觉：

- 两侧（或一侧）因 `ORDER BY` / 索引顺序**已经有序**，排序成本被摊掉。
- 范围条件、非等值在某些系统里比 Hash 好处理（视实现而定）。

代价特征：排序（或外部排序）往往主导；有序输入时归并很便宜。

---

## 6. Join 顺序：算法绑在「谁先谁后」上

> 三表及以上时，顺序与算法一起枚举。左深树是常见搜索限制：每次只把一张新表接到当前结果上。

```text
# 左深
((A ⋈ B) ⋈ C) ⋈ D

# bushy（许多优化器默认不搜或少搜）
(A ⋈ B) ⋈ (C ⋈ D)
```

例子：小表 `users`（已滤 CN）先与 `orders` 做 Index NLJ，再拿结果去驱动 `products`——中间结果若控制得住，整条链都是「小 Outer × 索引 Inner」。若先把两张大表 Hash Join 再滤，可能完全另一番景象。  
**顺序问题本质上是基数问题**，交给[第五篇](/database/mysql/cost-model-and-plan-search/)的估计与搜索。

---

## 7. 本篇对齐

| 名词 | 含义 |
|---|---|
| 访问路径 | 单表行如何从存储取出（全表 / 索引 / 覆盖 / 是否回表） |
| NLJ | 外表逐行，内表探测；有索引时内层是 Lookup |
| Hash Join | 一侧建哈希表，另一侧探测；利等值、利无索引大表 |
| Sort-Merge | 两侧按键有序后归并匹配 |
| 物理计划 | 上述选择绑定后的算子树，供执行器直接跑 |

下一篇回答：候选这么多，**凭什么说 A 比 B 便宜**，以及搜不全时怎么剪枝——[代价模型与计划搜索](/database/mysql/cost-model-and-plan-search/)。
