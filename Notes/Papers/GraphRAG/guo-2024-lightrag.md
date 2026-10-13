---
title: Guo 等：把图索引进向量检索，并做成增量
createTime: 2026-10-14
author: ZQ
tags:
  - Papers
  - GraphRAG
permalink: /notes/papers/graphrag/guo-2024-lightrag/
---

@[pdf height="80vh" width="100%"](/papers/graphrag/guo-2024-lightrag.pdf)

Guo 等人的 *LightRAG: Simple and Fast Retrieval-Augmented Generation*（arXiv:2410.05779）保留「实体—关系图」这个索引，但查询不再走社区摘要。图上的实体和关系各自带一段描述，检索时同时用向量找近邻、用图找相邻节点，两路结果合在一起交给生成。

增量更新是它相对 GraphRAG 的主要取舍：新文档只抽出自己的实体和关系并入图，不重建全局社区。换来的是没有那层「先读完全库再回答」的摘要；问题如果真的要全局综合，这套索引覆盖不到 GraphRAG 的社区层。
