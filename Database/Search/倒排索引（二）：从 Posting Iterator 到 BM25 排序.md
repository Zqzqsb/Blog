---
title: 倒排索引（二）：从 Posting Iterator 到 BM25 排序
createTime: 2026-09-14
author: ZQ
tags:
  - 搜索引擎
  - 倒排索引
  - Lucene
  - BM25
permalink: /database/search/inverted-index-query-bm25/
---

> Term Dictionary 找到的不是最终结果，而是几条等待消费的 Posting Iterator。查询执行器要让这些有序流完成 AND、OR 与 Phrase 匹配，再用 tf、df 和字段长度计算 BM25。本文继续使用四篇中文文档，逐步走完从查询字符串到排名分数的数据流。

<!-- more -->

---

本文是倒排索引系列的第二篇：

1. [从 CJK 分词到 Term Dictionary 与 Posting List](/database/search/inverted-index/)
2. **从 Posting Iterator 到 BM25 排序**（本文）
3. [WAND、Block-Max 与 Top-K 动态剪枝](/database/search/inverted-index-top-k-pruning/)

## 1. 查询不是拿字符串直接查词典

> 索引期定义了 term，查询解析层通常要把用户文本带回同一套词项空间。Posting Iterator 的起点不是界面上的原句，而是已经生成的查询树。

沿用第一篇的 `title` 字段：

```text
doc 0: 数据库索引原理
  → [数据库@0, 索引@1, 原理@2]

doc 1: 数据库索引优化与数据库实践
  → [数据库@0, 索引@1, 优化@2, 数据库@3, 实践@4]

doc 2: 数据仓库索引设计
  → [数据仓库@0, 索引@1, 设计@2]

doc 3: 数据库查询优化
  → [数据库@0, 查询@1, 优化@2]
```

用户输入：

```text
数据库索引
```

若查询 Analyzer 同样得到 `[数据库, 索引]`，查询解析器还要决定两者的关系：

```text
title:数据库 AND title:索引
title:数据库 OR  title:索引
title:"数据库 索引"
```

三者使用同样两个 term，执行语义却不同：

- AND 要求两条 docID 流对齐。
- OR 接受任意一条命中，并累加命中 term 的分数。
- Phrase 先做 AND 近似召回，再读取 positions 验证相邻关系。

若字段使用 CJK bigram，原查询可能变成 `数据、据库、库索、索引`，查询树和 posting 数量也会随之改变。Analyzer 不只是写入阶段的细节，它直接决定一次查询要打开多少条倒排表。

但「查询一定自动走 Analyzer」也不成立。Query Parser、Match Query 等文本查询通常负责分析输入；直接构造 `new TermQuery(new Term("title", "数据库"))` 时，传入的已经是最终 term bytes，不会再调用 Analyzer。`PrefixQuery` / `WildcardQuery` 的模式也不能默认按普通全文文本重新分词。调用层必须知道自己提交的是原始文本还是索引词项。

---

## 2. Posting Iterator：查询执行器看到的接口

> Posting List 是存储结构；Posting Iterator 是执行时消费它的方式。压缩、skip data 和文件偏移都藏在迭代器之后。

可以把 Lucene 风格的文档迭代接口简化为：

```text
docID()           当前文档
nextDoc()         移到下一篇文档
advance(target)   移到第一篇 docID >= target 的文档
cost()            估计需要遍历的文档数
```

Lucene 中，词项级 `PostingsEnum` 本身继承 `DocIdSetIterator`；一个复合 Query 的 `Scorer.iterator()` 也返回相同的 docID 递增接口。底层单词倒排和上层 AND / OR scorer 因而可以用同一种推进协议组合。

对 `(title, 数据库)`：

```text
postings = [0, 1, 3]

nextDoc()      → 0
nextDoc()      → 1
advance(3)     → 3
advance(4)     → NO_MORE_DOCS
```

调用者不需要知道 `[0,1,3]` 在磁盘上是 Variable-Byte、FOR 还是其他块编码。迭代器按需解码当前块，`advance` 则利用 skip data 跨过不可能命中的块。

`cost()` 不是精确运行时间。它通常更接近迭代器预计产出的文档数，可帮助查询规划选择较稀有的 term 作为前导条件。

### 2.1 单词查询

查询 `title:数据库`：

```text
Query Analyzer
  → term "数据库"
  → Term Dictionary.seekExact
  → docFreq=3，打开 Posting Iterator
  → 依次返回 doc 0、1、3
```

此时只判断命中的工作量大致随 `docFreq` 增长。词典 seek 很快，不代表后面的 posting 很短；一个命中全库的高频词仍可能昂贵。

---

## 3. 多词查询就是多条有序流的协同推进

示例 postings：

```text
数据库 → [0, 1, 3]
索引   → [0, 1, 2]
优化   → [1, 3]
```

### 3.1 AND：让迭代器在同一个 docID 对齐

`数据库 AND 索引` 的推进过程：

```text
数据库: 0  1  3
索引:   0  1  2
        ✓  ✓
```

结果为 `[0, 1]`。在一般情况下：

1. 先从估计最短的 posting 取一个候选 docID。
2. 让其他迭代器 `advance(candidate)`。
3. 全部停在同一 docID 时收集；否则把落后的迭代器继续推进。

![AND 查询的 Posting Iterator 推进过程](./倒排索引：从%20Posting%20List%20到%20BM25%20与动态剪枝.assets/postings-intersection.svg)

当两条列表长度差异很大时，这比同步逐项扫描更省。例如稀有词只有 100 个 docID，高频词有一千万项，查询可以让稀有词给出 100 个候选，高频词反复 `advance(target)`。

### 3.2 OR：归并时还要记住谁命中了

`数据库 OR 索引` 的并集为：

```text
doc 0: 数据库 + 索引
doc 1: 数据库 + 索引
doc 2: 索引
doc 3: 数据库
```

如果只求所有 docID，可以像归并多个有序数组一样用最小堆推进。若还要相关性排序，执行器必须保留同一 docID 命中了哪些 term，因为各 term 的评分贡献需要累加。

OR 的困难通常不在合并本身，而在高频 term 让并集接近全库。即使最终只返回 10 条，朴素执行仍可能为数百万篇文档计算分数。第三篇的 WAND 与 Block-Max 正是为此服务。

### 3.3 NOT 与 Filter：排除条件通常不贡献分数

查询：

```text
数据库 AND NOT 实践
```

可以让「数据库」产生候选 `[0,1,3]`，再用「实践」的 `[1]` 排除 doc 1，得到 `[0,3]`。

结构化过滤条件也常作为候选门槛，而不进入 BM25。例如：

```text
title:数据库 AND status:published
```

`status` 可以使用倒排或 bitset 判断是否允许该 docID；标题 term 负责相关性贡献。把 Filter 与 Scorer 分开，能让缓存、布尔执行和评分职责更清楚。

---

## 4. Phrase：docID 命中只是近似结果

> `"数据库 索引"` 不只要求两个 term 在同一文档，还要求它们的位置满足短语约束。

先对 docID posting 求交：

```text
数据库 → [0, 1, 3]
索引   → [0, 1, 2]
共同文档 → [0, 1]
```

再读取共同文档的位置：

```text
doc 0:
  数据库 positions=[0]
  索引   positions=[1]
  存在 1 = 0 + 1，匹配

doc 1:
  数据库 positions=[0, 3]
  索引   positions=[1]
  存在 1 = 0 + 1，匹配
```

`doc 3` 有「数据库」但没有「索引」，第一阶段就被淘汰；系统不必为它解码位置。

这是典型的 two-phase execution：

```text
approximation：便宜的 docID 交集
confirmation：昂贵的 positions 校验
```

带 `slop` 的 Phrase、Span 查询、地理形状或脚本条件也可能采用类似结构：先用一个宽松条件召回，再对少量候选做精确验证。

如果索引没有保存 positions，系统无法仅凭 docID posting 精确回答短语查询。回读原文重新分词理论上可做，但会失去倒排查询的性能和一致性优势。

---

## 5. Prefix、Wildcard 与 Regex：先展开 term，再处理 postings

查询：

```text
title:数据*
```

不会直接对应一条 posting。概念上，它覆盖一个有序 term 范围：

```text
lower bound: "数据"
  → 数据仓库
  → 数据库
upper bound: 第一个不再以“数据”开头的 term
```

然后将这些 term 重写或流式执行为多分支查询：

```text
title:数据仓库 OR title:数据库
```

Lucene 实际不会在找到下界后无条件顺扫完整词典。`PrefixQuery`、Wildcard / Regex 会编译为自动机，`Terms.intersect()` 联合遍历自动机状态与 BlockTree，跳过不可能匹配的 term block 和 floor block。若模式类似 `*库*`、缺少固定前缀且命中 term 极多，访问范围仍可能很大。

上面的 OR 只表达逻辑展开，不代表 Lucene 默认逐 term 计算 BM25。`PrefixQuery` / `WildcardQuery` 默认采用 constant-score blended rewrite；若显式选择 scoring rewrite，才需要面对大量 term 独立评分以及 Boolean clause 数量等限制。

因此，多词项查询有两层成本：

1. **词典展开成本**：产生多少个 term。
2. **postings 执行成本**：这些 term 一共覆盖多少文档。

限制 expansion 数量、选择 constant-score rewrite，或预先建立 edge-ngram 字段，本质上都是在改变这两层成本和相关性语义。

---

## 6. 从匹配集合到相关性分数

> 倒排索引回答「哪些文档包含查询词」；BM25 回答「这些文档谁更值得排在前面」。

对某个查询 term，现有结构能提供：

```text
tf(t, D)       当前 posting 中的 freq
df(t)          Term Dictionary 中的 docFreq
N              字段中有值的文档数
|D|            norms 编码的当前字段长度
avgdl          全局字段总 token 数 / 文档数
```

![BM25 的输入分别来自哪里](./倒排索引（二）：从%20Posting%20Iterator%20到%20BM25%20排序.assets/bm25-inputs.svg)

BM25 把它们组合为每个 term 的贡献，再对查询中的 term 求和。一种常见写法是：

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

- `IDF` 让稀有 term 权重更高；
- `tf` 增加会提高分数，但收益逐渐饱和；
- `|D|/avgdl` 抑制长字段仅因 token 多而占优；
- `k1` 控制 tf 饱和速度；
- `b` 控制长度归一化强度。

BM25 不是倒排索引本身。同一套 postings 可以供 Boolean、TF-IDF、BM25、语言模型或学习排序特征使用；只是 BM25 恰好能消费现有的 freq、docFreq 和 norms。

---

## 7. 手算一次 BM25

> 公式只有代入具体数据，才能解释为什么 posting 要保存 freq、词典要保存 docFreq、字段还要单独保存 norms。

查询：

```text
数据库 索引
```

采用：

```text
k1 = 1.2
b  = 0.75
N  = 4
```

四篇文档的 token 长度为：

```text
doc 0: [数据库, 索引, 原理]                       dl=3
doc 1: [数据库, 索引, 优化, 数据库, 实践]         dl=5
doc 2: [数据仓库, 索引, 设计]                     dl=3
doc 3: [数据库, 查询, 优化]                       dl=3

avgdl = (3 + 5 + 3 + 3) / 4 = 3.5
```

两个查询词都出现在 3 篇文档中：

```text
df(数据库) = 3
df(索引)   = 3
```

使用 Lucene BM25Similarity 采用的 IDF 形式：

$$
\operatorname{IDF}(t)
=
\ln\left(1+\frac{N-df(t)+0.5}{df(t)+0.5}\right)
$$

代入后两者的 IDF 都是：

$$
\ln\left(1+\frac{4-3+0.5}{3+0.5}\right)
\approx 0.3567
$$

### 7.1 长度为 3、tf 为 1

doc 0、doc 2、doc 3 对各自命中 term 都属于这种情况：

$$
K
=1.2\left(1-0.75+0.75\frac{3}{3.5}\right)
\approx1.0714
$$

单个 term 贡献：

$$
0.3567\times\frac{1\times2.2}{1+1.0714}
\approx0.3788
$$

所以：

```text
doc 0 同时命中两个词：0.3788 + 0.3788 = 0.7576
doc 2 只命中“索引”：0.3788
doc 3 只命中“数据库”：0.3788
```

### 7.2 长度为 5，且「数据库」出现两次

doc 1 的长度归一化项为：

$$
K
=1.2\left(1-0.75+0.75\frac{5}{3.5}\right)
\approx1.5857
$$

「数据库」的 `tf=2`：

$$
0.3567\times\frac{2\times2.2}{2+1.5857}
\approx0.4377
$$

「索引」的 `tf=1`：

$$
0.3567\times\frac{1\times2.2}{1+1.5857}
\approx0.3035
$$

总分：

```text
doc 1 = 0.4377 + 0.3035 = 0.7412
```

最终顺序：

```text
doc 0  0.7576
doc 1  0.7412
doc 2  0.3788
doc 3  0.3788
```

doc 1 中「数据库」出现两次，却没有超过更短的 doc 0。这同时体现了两件事：

- tf 从 1 增至 2 有收益，但不是线性翻倍；
- 更长字段受到更强的长度归一化。

### 7.3 稀有词为什么能改变排名

把查询改成：

```text
数据仓库 索引
```

`数据仓库` 只出现在 doc 2，`df=1`：

$$
\operatorname{IDF}(\text{数据仓库})
=
\ln\left(1+\frac{4-1+0.5}{1+0.5}\right)
\approx1.2040
$$

它的权重远高于 `df=3` 的「索引」。doc 2 同时命中稀有实体和常见词，分数约为：

```text
1.2787 + 0.3788 = 1.6575
```

这就是 IDF 的直觉：一个几乎每篇文档都有的词区分度低，一个只在少数文档出现的词更能解释用户意图。

---

## 8. 现实中的 Lucene BM25 还多了哪些边界

上面的计算用于解释数据流，现实实现还要注意：

- 本文采用教科书常见的 `tf(k1+1)/(tf+K)` 形式。Lucene 10.5.1 的 `BM25Similarity` 实际使用 `tf/(tf+K)`，省略对所有 term 都相同的常数因子 `k1+1=2.2`。因此本例 Lucene 尺度约为 `doc0=0.3444、doc1=0.3369、doc2=doc3=0.1722`，排名不变，但不能把前文手算值原样当成 Elasticsearch `_score`。
- Lucene 的字段长度来自 norms 的紧凑编码，不应假设总能无损还原原始 token 数。
- `discountOverlaps` 会影响 position increment 为 0 的重叠 token 是否计入长度；同义词展开常涉及这个边界。
- `N` 使用包含该字段的 `docCount`，`avgdl=sumTotalTermFreq/docCount`，不是无条件使用整个索引的文档数；稀疏字段尤其容易混淆。
- `docFreq`、文档数和字段统计由当前 `IndexReader` 视图提供，新增 Segment、删除或 Merge 后数值可能变化。
- 字段只索引 DOCS、不保存 freq 时，命中词频按 1 处理；关闭 norms 时则失去字段长度归一化。
- 多字段查询通常分别评分后按 boost 或查询结构组合，不能把 `title` 与 `body` 的字段长度直接混成一项。
- 删除、缺失 norms、自定义 Similarity 和搜索引擎外层的 function score 都可能改变最终分数。

最重要的仍是：Analyzer 改变 token 后，tf、df、dl 和 avgdl 会一起变化。相关性调优不能只盯着 `k1/b`，忽略索引期语义。

---

## 9. BM25 算完了，为什么还需要动态剪枝

朴素 OR Top-K 可以这样执行：

```text
枚举所有匹配 docID
  → 解码 freq / norms
  → 计算每个 term 的 BM25
  → 累加精确分数
  → 放入大小为 K 的结果堆
```

若查询 term 的并集有一千万篇文档，而用户只看前 10 条，绝大多数精确打分最终都会被丢弃。

一旦结果堆里已经有较强文档，当前第 10 名分数就形成 `minCompetitiveScore`。如果某个候选或整个 docID 块的理论最高分仍达不到阈值，它就不必完整评分。

这进入系列第三篇：

[倒排索引（三）：WAND、Block-Max 与 Top-K 动态剪枝](/database/search/inverted-index-top-k-pruning/)

---

## 延伸阅读

- [Lucene BM25Similarity](https://lucene.apache.org/core/10_5_1/core/org/apache/lucene/search/similarities/BM25Similarity.html)：Lucene 的 IDF、tf 归一化与 norms 行为。
- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/)：Boolean retrieval、词项统计与相关性模型。
- [Lucene Query API](https://lucene.apache.org/core/10_5_1/core/org/apache/lucene/search/package-summary.html)：Weight、Scorer、DocIdSetIterator 与 TwoPhaseIterator 的执行抽象。
- [Elasticsearch multi-term query rewrite](https://www.elastic.co/docs/reference/query-languages/query-dsl/multi-term-rewrite)：Prefix、Wildcard 等多词项查询的 rewrite 方式。
