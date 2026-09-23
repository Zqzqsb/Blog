---
title: 倒排索引（三）：WAND、Block-Max 与 Top-K 动态剪枝
createTime: 2026-09-14
author: ZQ
tags:
  - 搜索引擎
  - 倒排索引
  - Lucene
  - WAND
  - Block-Max
permalink: /database/search/inverted-index-top-k-pruning/
---

> BM25 能算出相关性，不代表每篇命中文档都值得精确打分。Top-K 搜索只关心前几名：结果堆产生竞争阈值，WAND 用 term 级分数上界跳过不可能竞争的 docID，Block-Max 再把上界缩小到局部块。只要上界安全，被跳过的文档就不可能进入 Top-K，最终排名仍然精确。

<!-- more -->

---

本文是倒排索引系列的第三篇：

1. [从 CJK 分词到 Term Dictionary 与 Posting List](/database/search/inverted-index/)
2. [从 Posting Iterator 到 BM25 排序](/database/search/inverted-index-query-bm25/)
3. **WAND、Block-Max 与 Top-K 动态剪枝**（本文）

## 1. 真正昂贵的不是公式，而是候选数量

> BM25 对一篇文档只做少量算术；当 OR 查询的 postings 并集覆盖数百万文档时，「少量算术 × 数百万」才成为问题。

查询：

```text
数据库 OR 索引 OR 优化
```

朴素执行过程是：

```text
归并三条 posting iterator
  → 枚举每个命中 docID
  → 解码 freq 与 norms
  → 计算每个命中 term 的精确 BM25
  → 累加总分
  → 尝试放入 Top-K 堆
```

假设并集命中 500 万篇文档，但用户只取前 10 条。最终有 4,999,990 个分数被算出后丢弃。

优化目标不是换一个近似评分公式，而是回答：

> 能否在不计算精确分数的前提下，证明某篇文档的最高可能分数也进不了前 10？

这需要两个量：

1. 当前 Top-K 的最低竞争分数；
2. 尚未完整评分的候选能达到的安全上界。

---

## 2. Top-K 堆怎样产生竞争阈值

维护一个容量为 `K` 的最小堆：

```text
K = 3

当前结果：
doc 17  score=5.8
doc 42  score=4.6
doc 9   score=3.1  ← 堆顶
```

此时：

```text
minCompetitiveScore = 3.1
```

新候选只有精确分数高于 3.1 才能替换堆顶。若某候选的理论上界只有 2.7，直接跳过不会改变 Top-3。

堆未满时通常还没有有效阈值，剪枝能力很弱。随着较强文档进入结果集，堆顶不断升高，后半程能跳过更多候选。这就是「动态」剪枝：阈值由查询运行过程中已经找到的结果推动。

### 2.1 上界可以松，不能错

设真实分数为 `score(D)`，用于剪枝的值必须满足：

$$
\operatorname{upperBound}(D) \ge \operatorname{score}(D)
$$

- 上界过高只是少跳一些文档，影响性能。
- 上界低于真实分数可能把本应进入 Top-K 的文档剪掉，破坏正确性。

在本文讨论的非负、可加 BM25 贡献下，只要上界确实安全、阈值没有被人为放大，WAND 系算法得到的仍可是**精确 BM25 Top-K**。原始 WAND 也存在主动放宽阈值的近似用法，不能仅凭算法名断言精确。它与 ANN 的常规近似召回仍有区别：安全模式只跳过已经被数学上界证明不可能竞争的候选。

并列分数还要服从 Collector 的 tie-break 规则。实现通常会让比较关系和浮点上界保持保守，宁愿多评一个候选，也不能误剪。

---

## 3. term 级最大贡献从哪里来

对查询中的每个 term，Scorer 可以给出一个最大分数：

```text
数据库  maxScore = 2.0
索引    maxScore = 1.3
优化    maxScore = 0.9
```

含义不是「每篇命中文档都得这些分」，而是：

```text
任意文档来自“数据库”的贡献 <= 2.0
任意文档来自“索引”的贡献   <= 1.3
任意文档来自“优化”的贡献   <= 0.9
```

BM25 的 term 上界可由当前查询 boost、IDF、可达到的 tf 饱和值和最有利的长度归一化构造。现实 Lucene scorer 会通过 impact 数据、`advanceShallow` 与 `getMaxScore(upTo)` 暴露某个 docID 范围内的安全上界，而不是每次从公式临时猜测。这类剪枝只在收集模式允许竞争式 Top-K（如 `ScoreMode.TOP_SCORES`）时启用；要求遍历全部匹配的模式不能直接照搬。

三个 term 的全局总上界为：

```text
2.0 + 1.3 + 0.9 = 4.2
```

若当前阈值已高于 4.2，后面任何文档都不可能竞争，整个查询可以提前结束。更多时候总上界仍然较高，但某些 docID 只可能命中其中一两个 term；WAND 利用各 iterator 的当前位置判断它们是否有机会对齐。

---

## 4. WAND：用 pivot 决定谁需要追上来

> WAND 不要求所有 iterator 同步逐项推进。它按当前 docID 排序，累加 term 上界，找到第一个可能超过阈值的 pivot。

为便于观察，使用三条合成 postings：

```text
A 数据库  docs=[2, 5, 9, 12]   maxScore=2.0
B 索引    docs=[1, 5, 8, 12]   maxScore=1.3
C 优化    docs=[3, 5, 7, 12]   maxScore=0.9

minCompetitiveScore = 3.0
```

### 4.1 第一轮：pivot 在 doc 2

按当前 docID 排序：

```text
B@1  upper=1.3   累计=1.3
A@2  upper=2.0   累计=3.3  ← 首次达到阈值，pivot=2
C@3  upper=0.9
```

doc 1 只可能命中 B，最高 1.3，不可能竞争。位于 pivot 之前的 B 可以直接：

```text
B.advance(2) → B@5
```

WAND 没有给 doc 1 计算精确分数。

### 4.2 第二轮：pivot 前移到 doc 5

当前位置变为：

```text
A@2  upper=2.0   累计=2.0
C@3  upper=0.9   累计=2.9
B@5  upper=1.3   累计=4.2  ← pivot=5
```

在 doc 5 之前：

- doc 2 只可能得到 A 的 2.0；
- doc 3 只可能得到 C 的 0.9；
- 即使某个未显示位置让 A 与 C 同时命中，总上界也只有 2.9。

它们都达不到阈值 3.0，因此 pivot 之前的 A、C 可以直接追到 5：

```text
A.advance(5) → A@5
C.advance(5) → C@5
```

### 4.3 第三轮：三个 iterator 在 doc 5 对齐

```text
A@5
B@5
C@5
```

doc 5 的理论上界为 4.2，确实有竞争可能，这时才解码必要的 freq、norms 并计算精确分数。

假设：

```text
score_A(doc5)=1.7
score_B(doc5)=1.0
score_C(doc5)=0.6

total=3.3
```

3.3 超过阈值 3.0，doc 5 进入结果堆，并可能把 `minCompetitiveScore` 继续抬高。

### 4.4 WAND 跳过了什么

WAND 跳过的不是「不匹配」文档，而是**可能匹配、但最高分也不够高**的文档。布尔 OR 的完整命中集合并没有被枚举完，这也是精确 total hits 与动态剪枝之间存在张力的原因。

---

## 5. 为什么 term 全局上界仍然太松

假设「数据库」只有一篇极短文档出现很多次，得到全局 `maxScore=2.0`。这一个离群点会让整条 posting 在所有位置都背着 2.0 的上界，即使绝大多数区域的实际最高贡献只有 0.5。

```text
数据库 postings:

doc 0..127     区域最大贡献 0.8
doc 128..255   区域最大贡献 1.9
doc 256..383   区域最大贡献 0.5

term 全局上界 = 2.0
```

只看全局上界时，每个区域都像「可能出现 2.0」。上界虽然安全，却不够紧，很多本可跳过的区域仍会进入 WAND 调度。

---

## 6. Block-Max：把上界缩小到当前 docID 块

> Block-Max 为 posting 的局部范围保存最大 impact。在 WAND 已找到可能竞争的 pivot / window 后，再用相关块的局部上界做二次判断，不再让其他区域的高分离群点影响当前范围。

块上界不能不加条件地替换 WAND 选 pivot 时的 term 全局上界：不同 posting 的块边界通常不对齐，当前块结束后、pivot 之前可能进入一个上界更高的新块。Block-Max WAND 会先用全局安全上界选择候选 pivot，再对相关 iterator 做 `advanceShallow`，以最早结束的有效边界形成共同 `upTo`，只在这个范围内累加局部上界；跨过边界后必须重新计算。

为突出第二次判断，下面假设已进入候选 window，且三个 term 在图中的概念区间恰好对齐：

```text
范围 0..127:
  数据库 max=0.8
  索引   max=0.6
  优化   max=0.4
  合计上界=1.8

范围 128..255:
  数据库 max=1.9
  索引   max=1.1
  优化   max=0.7
  合计上界=3.7

minCompetitiveScore=3.0
```

第一个范围即使三词同时取得块内最高贡献，也只有 1.8，整段可以跳过。第二个范围上界为 3.7，仍可能出现竞争文档，需要进入更细的 iterator 调度与精确评分。

![Block-Max 用局部上界跳过非竞争块](./倒排索引（三）：WAND、Block-Max%20与%20Top-K%20动态剪枝.assets/block-max-pruning.svg)

这里把各 term 的块画成对齐区间只是为了说明。现实 postings 的块边界、impact 分组和 scorer 可见的 shallow range 由编码格式与实现决定；安全结论只覆盖当前共同 `upTo`，不能无限延伸到后面的块。

### 6.1 impact 不只是 tf

对 BM25 来说，term 分数受多项因素影响：

```text
query boost
IDF
freq
字段长度 norm
```

同样 `tf=3` 的 posting，短字段通常比长字段贡献高。因此 block-max 元数据需要保存足以推导安全分数上界的 impact 信息，而不只是块内最大 tf。

Lucene 也不是把某个版本 BM25 算出的浮点 `maxScore` 直接固化进索引。它在 skip/impact 元数据中保留可能形成最大贡献的 `(freq, norm)` 组合，去掉那些「freq 更低且字段更长」的支配项；查询时再由当前 Similarity、IDF 与 boost 把这些 impact 转成分数上界。这样更换评分参数时不必重建一份绑定旧公式的 max-score 索引。

索引期保存更细上界会增加少量空间和写入工作；查询期则能减少 freq/norm 解码与精确评分。这仍是典型的空间换时间。

---

## 7. WAND、Block-Max WAND 与 MAXSCORE 不要混成一个名字

三者目标相同：利用分数上界避免无效评分；调度方式不同。

### 7.1 WAND

WAND 根据各 posting iterator 的当前 docID 和 term 级上界寻找 pivot：

```text
按当前 docID 排序
  → 累加上界
  → 找到可能竞争的 pivot
  → 让 pivot 前的 iterator 跳跃
```

它能少评很多候选，但维护顺序、寻找 pivot 和频繁推进也有调度成本。

### 7.2 Block-Max WAND

Block-Max WAND 保留 WAND 的全局上界与 pivot 选择，再 shallow-advance 到相关块，用局部上界做第二层验证。局部上界更紧，可以一次跳过当前共同边界内不可能竞争的范围；它不是简单把 pivot 阶段的全局上界全部替换掉。

### 7.3 MAXSCORE

MAXSCORE 按各 term 的最大贡献把查询子句划分为：

- **essential**：必须先参与候选生成；
- **non-essential**：先不读取，只有候选仍有机会超过阈值时才补算。

若 non-essential 子句的上界之和也无法改变竞争结论，就不必访问它们。随着阈值上升，更多低上界子句可进入 non-essential 集合。

### 7.4 Block-max MAXSCORE

block-max MAXSCORE 使用局部块上界动态调整 essential / non-essential 划分。它同样利用 impact 数据，但执行循环不必与论文中的经典 WAND pivot 完全一致。

从版本演进看，Lucene 8.0 发布了带 block-max 索引支持的 WAND 优化；之后又因 MAXSCORE 在难以剪枝、K 较大或 term 较多时单候选开销更低，从 Lucene 9.4 开始让部分顶层 disjunction 使用 block-max MAXSCORE。Lucene 9.9 又增强了 MAXSCORE：阈值足够高时，不只把低贡献 term 延迟评分，还能要求候选同时命中若干高贡献 term。版本号用于理解演进，不应替代对当前查询实际 Scorer 的检查。

Lucene 不同版本和查询形态可能选择不同 scorer。阅读源码或性能日志时，应区分：

```text
索引格式提供了什么 block / impact 元数据
Scorer 对外提供什么 max-score 能力
BooleanQuery 当前实际选择哪种执行循环
```

「用了 block-max 元数据」不等于执行器一定在运行某篇论文的原始 Block-Max WAND 伪代码。

---

## 8. 动态剪枝什么时候效果好

剪枝收益取决于查询和数据分布。

### 8.1 容易剪枝

- 只取较小的 K，例如 Top-10。
- 查询早期能找到高分文档，阈值迅速升高。
- 各块分数分布差异大，局部上界明显低于全局上界。
- OR 分支多，但大量分支贡献上限很低。
- 索引排序或数据布局让高质量候选较早出现。

### 8.2 不容易剪枝

- 结果堆尚未填满，阈值接近最低值。
- K 很大，最后一名分数很低。
- 所有候选分数接近，上界长期高于阈值。
- 上界过松，极端高分文档抬高许多块。
- 查询要求精确统计所有命中。
- 自定义评分无法提供可靠 `maxScore`。

因此不能只问「是否支持 WAND」，还要观察候选数量、被完整评分数量、块跳过率、K 和 total-hits 配置。

---

## 9. 精确 Top-K 不等于精确 total hits

> 对排名而言，低分文档可以安全跳过；对命中总数而言，它们仍然是一次合法匹配。

若 API 只要求：

```text
返回分数最高的 10 篇文档
```

动态剪枝可以不枚举所有低分匹配，Top-10 仍精确。

若同时要求：

```text
精确返回 totalHits=5,237,891
```

系统必须确认每个匹配文档是否存在。仅凭「分数不够竞争」不能把它从计数里忽略，因此很多跳跃机会会消失，或需要额外计数路径。

Lucene Collector 可以使用 `totalHitsThreshold` 表达「计数到某个阈值后允许只给下界」。上层常见输出语义类似：

```text
value: 10000
relation: GREATER_THAN_OR_EQUAL_TO
```

这不是搜索少返回了 Top-K，而是总命中数只承诺「至少这么多」。需要精确数量时，应明确接受对应的查询成本。

---

## 10. 哪些查询会限制 max-score 优化

动态剪枝建立在「可组合的安全上界」之上，以下情况要额外处理：

- **Phrase / Span**：docID posting 只是 approximation，还需 positions confirmation；上界必须覆盖最终精确 scorer 的贡献。
- **Filter**：通常只决定候选是否允许，不贡献正分；它可以缩小集合，但不能被当作普通 term 上界相加。
- **负分或非单调自定义函数**：若 scorer 无法给出可靠上界，执行器应禁用相应优化，而不是冒险剪枝。
- **脚本评分 / 外部特征**：读取代价高，若没有廉价上界，往往只能在较早阶段先缩小候选。
- **按字段排序而非 `_score`**：优化目标会转为比较排序值，可能使用 index sorting、early termination 等另一套机制。
- **`min_score`**：它是结果过滤阈值，不自动等价于所有 scorer 都能利用的块级安全上界。

优化是否启用是 scorer 能力与查询树共同决定的，不是索引级总开关。

---

## 11. 分片 Top-K：每个 shard 都运行自己的竞争

分布式搜索通常按 shard 保存若干 Lucene index：

```text
Coordinator
  → shard 0：本地 Top-K + 动态剪枝
  → shard 1：本地 Top-K + 动态剪枝
  → shard 2：本地 Top-K + 动态剪枝
  → 合并各 shard 候选，取 global Top-K
  → 回取命中文档内容
```

只要各 shard 使用可比较的同一评分语义，每个 shard 返回本地 Top-K 足以组成全局 Top-K 候选：若某文档连本 shard 前 K 都进不了，它前面已经有 K 篇更高分文档，也不可能进入全局前 K。

但 BM25 的统计可能是 shard-local：

```text
docFreq / docCount / avgdl
```

相同 term 在不同 shard 分布不均时，局部 IDF 会让分数尺度产生偏差。系统可以先收集全局统计再查询，或通过均匀路由减轻偏差；前者要多一次网络往返。

每个 shard 的 `minCompetitiveScore` 也独立演进。某个 shard 很快找到强候选，可能大量剪枝；另一个 shard 候选分数平坦，仍需完整评分许多文档。

---

## 12. 把三篇的数据流合起来

完整链路现在可以写成：

```text
索引期
  原始 CJK 文本
  → Analyzer 产生 term / position / offset
  → Term Dictionary 保存有序词项、统计和 postings 元数据
  → Posting List 按 docID 排序、分块、压缩并记录 impacts
  → 发布不可变 Segment

查询期
  查询 Analyzer
  → 在词典中 seek / enumerate term
  → Posting Iterator 执行 AND / OR / Phrase approximation
  → BM25 使用 tf / df / norms 计算相关性
  → Top-K 堆产生 minCompetitiveScore
  → WAND / MAXSCORE 利用安全上界跳过候选
  → Block-Max 利用局部 impact 跳过 docID 范围
  → Segment / shard 逐层归并 Top-K
```

最核心的三条因果关系是：

1. Analyzer 定义 term，因此也改变 tf、df、posting 长度和评分分布。
2. Posting 的有序与分块不仅服务压缩，也为 `advance` 和 block-max 跳跃提供物理边界。
3. BM25 给出精确分数，动态剪枝只决定哪些精确分数无需计算，不改变竞争结果。

倒排索引因此不是一个孤立容器，而是一组从语言边界、磁盘编码一直延伸到 Top-K Collector 的协同设计。

---

## 延伸阅读

- [Faster retrieval of top hits with Block-Max WAND](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand)：Block-Max WAND 进入 Lucene / Elasticsearch 的背景。
- [MAXSCORE & block-max MAXSCORE](https://www.elastic.co/search-labs/blog/more-skipping-with-bm-maxscore)：Lucene 从 WAND 到 block-max MAXSCORE 及后续改进。
- [From MAXSCORE to Block-Max WAND](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148045/)：Lucene impacts、正分约束与 total hits 取舍的实现背景。
- [Lucene Scorer API](https://lucene.apache.org/core/10_5_1/core/org/apache/lucene/search/Scorer.html)：`advanceShallow`、`getMaxScore` 与 `setMinCompetitiveScore`。
- [Lucene ImpactsDISI](https://lucene.apache.org/core/10_5_1/core/org/apache/lucene/search/ImpactsDISI.html)：基于 impacts 和最低竞争分数跳过非竞争文档。
- [Lucene TopScoreDocCollector](https://lucene.apache.org/core/10_5_1/core/org/apache/lucene/search/TopScoreDocCollector.html)：Top-K 收集与 total-hits threshold。
- [Efficient Query Evaluation Using a Two-Level Retrieval Process](https://dl.acm.org/doi/10.1145/956863.956944)：提出 WAND 的经典论文。
- [Faster Top-k Document Retrieval Using Block-Max Indexes](https://doi.org/10.1145/2009916.2010048)：Block-Max WAND 的经典论文。
