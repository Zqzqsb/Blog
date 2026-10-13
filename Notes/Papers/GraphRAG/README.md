---
title: GraphRAG
createTime: 2026-10-14
order: 2
author: ZQ
tags:
  - Papers
  - GraphRAG
permalink: /notes/Papers/graphrag/
---

这个领域收「先从文本建图，再沿图检索」的 RAG。三篇的差别在图上存什么、查询时走多远。

- [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](./1.edge-2024-graphrag.md)：社区摘要，服务需要通读全库的问题
- [LightRAG: Simple and Fast Retrieval-Augmented Generation](./2.guo-2024-lightrag.md)：图索引加向量，增量更新
- [HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models](./3.gutierrez-2024-hipporag.md)：图上的 Personalized PageRank，服务多跳
