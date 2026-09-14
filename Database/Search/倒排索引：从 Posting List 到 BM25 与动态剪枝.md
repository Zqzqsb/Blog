---
title: 倒排索引：从 Posting List 到 BM25 与动态剪枝
createTime: 2026-09-14
author: ZQ
tags:
  - 搜索引擎
  - 倒排索引
  - Lucene
  - BM25
  - WAND
  - Block-Max WAND
permalink: /database/search/inverted-index/
cover: /images/inverted-index-cover.jpg
---

![cover](/images/inverted-index-cover.jpg)

> 倒排索引把「文档包含哪些词」反转为「一个词出现在哪些文档」，使全文检索不必扫描全部正文。但真正的搜索引擎不只有 `term → docID[]`：词典负责定位倒排表，posting 携带词频与位置，BM25 把命中文档排出次序，WAND / Block-Max WAND 再利用分数上界跳过不可能进入 Top-K 的候选。本文沿一条查询的数据流，把这些结构串起来。

<!-- more -->

---

## 1. 为什么普通索引不够

> 全文检索的查询键不是一整列值，而是文档中数量不定、位置不定的词项集合。

设有三篇文档：

```text
doc 1: 向量数据库支持语义检索
doc 2: 搜索引擎使用倒排索引
doc 3: 数据库索引加速检索
```

按文档保存内容得到的是正排方向：

```text
docID → 文档内容 / 文档中的词
```

查「索引」时，如果只保留正排数据，就要依次打开三篇文档并检查内容。倒排索引把关系反过来：

```text
索引 → [doc 2, doc 3]
检索 → [doc 1, doc 3]
数据库 → [doc 1, doc 3]
```

查询先定位词项，再读取对应文档编号列表，工作量从「文档总数」收缩为「查询词命中的文档数」。

这和 B+ 树并不冲突：

| 结构 | 键从哪里来 | 擅长的查询 |
|---|---|---|
| B+ 树 | 一列完整、可排序的值 | 等值、范围、排序 |
| 哈希索引 | 一列完整值的哈希 | 等值 |
| 倒排索引 | 文档经分析后产生的多个词项 | 包含、布尔、短语、相关性 Top-K |

B+ 树可以索引完整标题，却不能自然表达「标题里任意位置出现某个词」；倒排索引为每个词项建立入口，代价是一次文档写入会展开成许多 posting。

还要避免一个同名误会：向量检索里的 IVF（Inverted File）也使用「中心 → 向量列表」的倒排组织，但键是聚类中心，候选依据是向量空间距离；本文的键是文本词项，候选依据是词法命中。二者共享「从键反查对象集合」的组织思想，不是同一种检索算法。

---

## 2. 最小数据模型：词典与倒排表

> 倒排索引至少由两层组成：`term → posting list 的位置`，以及有序的 posting list。

### 2.1 Term Dictionary：先找到词

词典保存一个 field 下所有不同词项及其统计、倒排表指针：

```text
term → {
  docFreq,
  totalTermFreq,
  postingsPointer
}
```

词典不能简单理解为内存哈希表。词项可能有千万级，既要支持精确查找，又要支持前缀、范围、通配符等按字典序枚举。Lucene 的 BlockTree Terms Dictionary 使用前缀树索引词块；FST（Finite State Transducer）可以通过共享前缀与后缀压缩词典或词项元数据。

词典回答的是：**词存不存在，posting list 在哪里**。

### 2.2 Posting List：再找到文档

每个词项对应一条按 `docID` 递增的列表。posting 不一定只有文档编号：

```text
term
  └─ posting[]
       ├─ docID       文档编号
       ├─ freq        该词在文档中的出现次数
       ├─ positions   出现位置
       ├─ offsets     原文字符区间
       └─ payload     可选的应用侧附加值
```

不同字段可以选择不同精度：

| 保存内容 | 能支持什么 | 代价 |
|---|---|---|
| 只存 docID | 是否包含词项 | 最省空间 |
| docID + freq | BM25 等词频相关评分 | 多一列整数 |
| docID + freq + positions | 短语、邻近查询 | 位置数据通常很大 |
| 再加 offsets / payload | 高亮、自定义打分 | 更多存储与解码 |

文档长度等字段级统计通常单独保存为 norms，不必在每个 posting 中重复。

---

## 3. 写入链路：正文如何变成倒排索引

> 写入不是把原字符串直接塞进词典，而是先定义「什么算同一个词」，再按词项聚合 posting。

### 3.1 Analyzer 决定索引语义

典型文本分析链路是：

```text
原始字段
  → Character Filter
  → Tokenizer
  → Token Filter
  → token(term, position, offsets)
```

- Character Filter 在切词前规范字符，例如处理 HTML 或字符映射。
- Tokenizer 决定边界；中文通常需要分词，而不是照搬英文空格切分。
- Token Filter 可做小写化、停用词、词干化、同义词扩展等。

例如 `Database indexes` 可能得到：

```text
database(position=0), index(position=1)
```

分析器不是无害的预处理：它直接定义了可搜索单位。索引期把 `databases` 归一成 `database`，查询期却不做同样归一化，就不可能命中。字段类型、语言和查询语义必须共同决定 analyzer。

### 3.2 从 token 流到 segment

![从文档到可查询 Segment](./倒排索引：从%20Posting%20List%20到%20BM25%20与动态剪枝.assets/indexing-pipeline.svg)

建索引时，系统为每篇文档分配 segment 内部的 `docID`，按 field 和 term 收集出现记录，再把同一 term 的记录按 docID 排序写出。数据太大时可分批生成有序块并归并；经典 SPIMI（Single-Pass In-Memory Indexing）就是按内存批次构建词典和倒排表，再合并磁盘块。

注意三种数据的职责不同：

- **倒排索引**：从词项找文档，用于召回和评分。
- **Stored Fields**：取回原文、标题等返回内容。
- **Doc Values**：面向列式访问，用于排序、聚合和脚本，不替代全文倒排。

---

## 4. 为什么 posting 必须有序且压缩

> 有序既让多词查询能线性合并，也让 docID 差分后变成大量小整数。

假设「索引」的 docID 列表为：

```text
[105, 107, 108, 130, 131]
```

保存相邻差值（d-gap）后变成：

```text
[105, 2, 1, 22, 1]
```

除第一个数外，大部分 gap 很小，更适合 Variable-Byte、FOR / PForDelta、SIMD-BP128 等编码。位置列表也可在单篇文档内做位置差分。

常见策略的取舍：

| 编码 | 核心思路 | 取舍 |
|---|---|---|
| Variable-Byte | 每 7 bit 数据配延续标记 | 简单、解码快，至少占整字节 |
| Frame of Reference | 一个块用固定 bit width | SIMD 友好，受块内最大值影响 |
| PForDelta | 大多数值定宽，异常值单独保存 | 兼顾压缩率与批量解码 |

压缩不一定让查询变慢：全文检索通常受内存层级与带宽限制。更小的倒排块能进入 page cache 和 CPU cache，批量解码成本可能低于搬运未压缩整数的成本。

长 posting list 还会建立多级 skip data。迭代器调用 `advance(target)` 时，可以跳到第一个不小于 `target` 的 docID，而不是逐项执行 `nextDoc()`。Lucene 的 postings 以块编码保存 docID、freq、position，并在跳跃元数据中关联相关文件偏移。

---

## 5. 查询执行：一条倒排表不难，多条才是算法

> 词典定位是入口；AND、OR、短语与 Top-K 的成本，取决于多条有序 posting 如何协同推进。

### 5.1 单词查询

查询 `database`：

```text
analyze query
  → term dictionary.seek("database")
  → 打开 postings(database)
  → 遍历 docID
```

成本大致随 `docFreq(database)` 增长。稀有词很便宜；停用词可能命中几乎全部文档，即使有索引也不便宜。

### 5.2 AND：有序列表求交

假设：

```text
database → [1, 3, 8, 11, 20]
index    → [2, 3, 7, 11, 18, 20]
```

双指针线性求交得到 `[3, 11, 20]`。列表长度严重不平衡时，通常从最短列表产生候选，让长列表用 `advance(target)` 跳跃；实现也可能使用 galloping / exponential search。

![AND 查询的 Posting Iterator 推进过程](./倒排索引：从%20Posting%20List%20到%20BM25%20与动态剪枝.assets/postings-intersection.svg)

这也是为什么 posting 按 docID 排序：布尔交集不需要哈希，也不必物化全部中间集合。

### 5.3 OR：并集不是简单拼接

OR 查询要合并多条有序流。若只求所有匹配文档，可用最小堆归并；若求相关性 Top-K，则每个候选还要累加各词项的评分。高频词一多，枚举所有并集成员会成为主要成本，WAND 系算法因此出现。

### 5.4 Phrase：先近似召回，再验证位置

短语 `"vector database"` 不只要求两个词出现在同一篇文档，还要求 position 相邻：

1. 先对 `vector` 与 `database` 的 docID posting 求交。
2. 只对共同文档读取 position。
3. 判断是否存在 `pos(database) = pos(vector) + 1`。

这是典型的 two-phase execution：便宜的 docID 交集是 approximation，昂贵的位置校验是 confirmation。若索引不保存 positions，无法仅靠倒排表精确回答短语查询。

### 5.5 Prefix / Wildcard / Regex

`data*` 先在词典中枚举 `data` 前缀下的词，再合并各自 posting。FST / BlockTree 的价值在这里更明显：查询可以把自动机与词典求交，跳过不可能匹配的词项分支，而不是扫完整词典。

---

## 6. BM25：从「命中」到「谁排前面」

> 倒排索引负责找到匹配文档；评分模型利用 posting 和全局统计对这些文档排序。

一种常见 BM25 形式为：

$$
\operatorname{score}(D,Q)
=
\sum_{t \in Q}
\operatorname{IDF}(t)
\cdot
\frac{tf(t,D)(k_1+1)}
{tf(t,D)+k_1\left(1-b+b\frac{|D|}{avgdl}\right)}
$$

其中：

- `tf(t,D)` 来自 posting 的词频；增加会提高分数，但收益逐渐饱和。
- `docFreq(t)` 与文档总数 $N$ 形成 IDF；稀有词贡献更大。
- $|D|/avgdl$ 做文档长度归一化，避免长文仅因词多占优。
- $k_1,b$ 控制词频饱和与长度惩罚。

这解释了倒排索引为什么还要保存 `freq`、norms 与 `docFreq`：它们不是为了判断「是否命中」，而是为了相关性排序。

BM25 不是倒排索引本身。TF-IDF、BM25、语言模型或学习排序都可以消费同一套倒排结构；反过来，改变 analyzer 会改变 term、tf、df，评分分布也会随之改变。

---

## 7. Top-K 动态剪枝：WAND 与 Block-Max

> 搜索通常只要前 10 条。若能证明某些候选的最高可能分数也进不了前 10，就没必要计算它们的精确分数。

### 7.1 最低竞争分数

维护大小为 $K$ 的结果堆。堆未满时阈值低；一旦装入较强结果，堆顶成为 `minCompetitiveScore`。此后只有理论最高分超过阈值的候选才值得完整评分。

关键是**上界必须安全**：可以高估，不能低估。只要剪枝依据的上界正确，WAND / MAXSCORE 返回的 Top-K 仍是精确的评分 Top-K；它们优化的是执行，不是把相关性结果改成近似。若系统同时跳过文档，总命中数可能只给下界或需要额外计算。

### 7.2 WAND

每个查询词有一个最大贡献上界。WAND 按当前 docID 排序各 posting 迭代器，累加上界寻找 pivot：

- 累计上界仍低于阈值：前面的迭代器可以向 pivot 跳跃。
- 累计上界超过阈值：该 pivot 才可能有竞争力，再做更完整的匹配与评分。

随着结果堆变强，阈值升高，更多候选可跳过。

### 7.3 Block-Max WAND / MAXSCORE

整条 posting 只存一个最大分，会被极端高分文档拖高，导致上界太松。Block-Max 把 posting 切成块，为每块记录最大 impact（由 tf、文档长度等决定）：

```text
term A postings:
  block 0 [doc 0..127]   maxScore = 0.7
  block 1 [doc 128..255] maxScore = 2.8
  block 2 [doc 256..383] maxScore = 0.4
```

若当前阈值是 1.5，且当前块内所有查询词的上界之和仍不到 1.5，整块可以跳过。局部上界不受别处离群点影响，比 term 级上界紧得多。

Lucene 8 引入了 BM25 兼容的 Block-Max WAND；后续版本在部分顶层 OR 查询中采用 block-max MAXSCORE。二者目标相同，调度方式不同：WAND 通常少评估更多候选但每次调度开销高，MAXSCORE 把词项分成 essential / non-essential，单次开销较低。具体选择属于查询执行器实现，不改变索引的基本数据模型。

---

## 8. 增量写入：不可变 segment 如何做到近实时

> 倒排表适合顺序、压缩、不可变存储；频繁在中间插入 docID 会破坏这些优势。Lucene 以多 segment 换近实时写入。

以 Lucene / Elasticsearch 为现实模型：

![Lucene 与 Elasticsearch 的 Segment 生命周期](./倒排索引：从%20Posting%20List%20到%20BM25%20与动态剪枝.assets/segment-lifecycle.svg)

- **Refresh**：把缓冲区内容写成可打开的新 segment，使其可搜索；不等于完整持久化提交。
- **查询**：在每个 segment 上各跑一次，过滤删除文档，再合并 Top-K。
- **更新**：写入新版本，同时把旧 docID 标记删除；倒排结构不原地改写。
- **删除**：先记录 live-doc bitmap，segment 合并时才物理清除。
- **Merge**：合并小 segment，重写词典与 postings，减少查询扇出并回收删除空间，但消耗磁盘 I/O 与 CPU。
- **Translog**：这是 Elasticsearch 在 Lucene 之外提供的恢复日志；不要把它误认成倒排索引文件。

不可变 segment 的收益是读路径几乎无需与写线程争锁，压缩布局稳定，也能充分利用 page cache。代价是写放大、短期删除空间和多 segment 查询开销。

---

## 9. 分布式与混合检索

### 9.1 分片 Top-K

分布式搜索通常按 shard 放置若干 Lucene index：

```text
Coordinator
  → 每个 shard 执行本地 query，返回 local Top-K
  → Coordinator 合并并取 global Top-K
  → 按 docID 回取文档内容
```

每个 shard 只返回少量候选，减少网络传输。但 BM25 的 df / 文档数若使用 shard 本地统计，分片分布不均时可能产生评分偏差；系统可通过全局统计预取或更均匀的路由缓解，代价是额外网络往返。

### 9.2 与向量检索组合

倒排检索擅长精确实体、术语、数字和可解释词项贡献；向量检索擅长语义近似。混合搜索常有三种执行形态：

| 形态 | 数据流 | 主要风险 |
|---|---|---|
| 并行召回 | BM25 Top-N 与 ANN Top-N 分别召回，再 RRF / 加权融合 | 两路分数不可直接比较 |
| 词法前置 | 倒排先过滤/召回，再做向量精排 | 语义相关但无关键词的文档进不了候选 |
| 向量前置 | ANN 召回，再用 BM25 / 规则精排 | 精确词项文档可能被 ANN 漏掉 |

这里的倒排索引与 HNSW / IVF 是两个检索器，不是「倒排索引里存向量」。它们可以共享文档 ID，在查询计划层汇合。向量索引的结构见 [向量索引算法全景](/database/vector/ann-index-landscape/)，向量压缩见 [向量索引量化全景](/database/vector/quantization-landscape/)。

---

## 10. 设计边界：它擅长什么，又放弃什么

> 倒排索引以词项为边界换来极快的稀疏召回；语义泛化、写放大与高频词长列表是对应代价。

| 场景 | 表现 | 原因 |
|---|---|---|
| 精确术语、编号、人名 | 强 | 词项可直接定位 |
| AND / OR / Phrase | 强 | posting 有序且可保存位置 |
| 前缀、通配符 | 可做但可能昂贵 | 需要展开多个 term |
| 高频停用词 | 容易昂贵 | posting 接近全库 |
| 同义表达、跨语言语义 | 原生较弱 | 不共享词项就无 posting 交集 |
| 高频更新 | 可近实时，但有写放大 | 新 segment + merge |
| 精确总命中数 + Top-K | 可能拖慢 | 动态剪枝难以跳过所有非竞争文档 |

因此，倒排索引的优化不是单个「算法」：

```text
Analyzer 定义词项
  → Term Dictionary 定位
  → Compressed Postings 召回
  → Boolean / Phrase 算法合并
  → BM25 评分
  → Block-Max 动态剪枝
  → Segment / Shard 汇总
```

改变其中一层，会把成本推向下一层。例如同义词在索引期展开会增大 postings，在查询期展开会增加 OR 分支；关闭 positions 能省空间，但短语查询随之失去精确依据。

---

## 11. 小结

倒排索引的核心映射只有一句：`term → postings`。它之所以能成为搜索引擎底座，是因为围绕这条映射补齐了一整条执行链：

1. Analyzer 把字符串变成稳定词项与位置。
2. 词典用前缀结构 / FST 快速定位 term 与倒排表。
3. postings 按 docID 排序，以 d-gap 和块编码压缩，并携带 freq / positions。
4. AND 用有序交集，Phrase 做位置验证，OR 进入 Top-K 评分。
5. BM25 利用 tf、df 与文档长度排序。
6. WAND / Block-Max 依据安全分数上界跳过不可能进入 Top-K 的文档块。
7. 不可变 segment、refresh、删除标记与 merge 把批量压缩结构接入近实时写入。
8. 分片在本地执行后合并，混合检索再与 ANN 在候选或排序层汇合。

理解这条链后，「倒排索引」就不再是一张 `word → docIDs` 的示意图，而是从文本语义边界一直延伸到 CPU cache、磁盘段和分布式 Top-K 的完整查询结构。

---

## 延伸阅读

- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)：倒排索引、布尔查询与压缩的经典教材。
- [Lucene BlockTree Terms Dictionary](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/codecs/lucene103/blocktree/Lucene103BlockTreeTermsReader.html)：词典与词块的现实实现。
- [Lucene Postings Format](https://lucene.apache.org/core/10_5_1/backward-codecs/org/apache/lucene/backward_codecs/lucene103/Lucene103PostingsFormat.html)：doc、freq、position、payload 与 skip data 的文件布局。
- [Faster retrieval with Block-Max WAND](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand)：动态剪枝进入 Lucene 的背景与效果。
- [Near real-time search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search)：segment、refresh 与近实时可见性。
