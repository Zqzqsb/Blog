---
title: Dange 等：对象存储上的 Serverless Postgres
createTime: 2026-10-14
author: ZQ
tags:
  - Papers
  - Lakebase
permalink: /notes/papers/lakebase/dange-pvldb2026-lakebase/
---

@[pdf height="80vh" width="100%"](/papers/lakebase/dange-pvldb2026-lakebase.pdf)

Dange 等人的 *Lakebase: Serverless Postgres over Open Lake Storage*（PVLDB 19(12): 4385–4398）写的是 Databricks 把 Neon 接到 Lakehouse 旁边之后的系统。计算节点仍是 PostgreSQL，本地不留持久数据；WAL 先到 Safekeeper 做多数派落盘，Pageserver 再把页物化进对象存储。

和 keynote 的口号相比，这篇把代价写清楚了：冷启动要靠预热池才压得住；PITR 窗口里的历史让存储大约放到逻辑库的数倍；分支链越深，读越要跨层，而且分支不能合并。外部引擎按 LSN 直接读页是可能的，但页解析和 MVCC 得自己做，复杂查询还是回到 Postgres 或湖表。
