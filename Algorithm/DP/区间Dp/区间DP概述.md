---
title: 区间DP概述
tags:
  - 算法
  - 动态规划
  - 区间DP
createTime: 2024-2-28
description: 这篇文章介绍了动态规划的概念和划分方法。
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/interval_dp/interval_dp_demo.png
author: ZQ
permalink: /algorithm/dp/interval_dp/
---

# 前言

在阅读本文之前，你需要阅读[动态规划概念](https://blog.zqzqsb.cn/2024/02/20/%E5%8A%A8%E6%80%81%E8%A7%84%E5%88%92%E6%A6%82%E5%BF%B5/)和[线性动态规划](<https://blog.zqzqsb.cn/2024/02/21/%E7%BA%BF%E6%80%A7%E5%8A%A8%E6%80%81%E8%A7%84%E5%88%92(%E4%B8%80)/>)。这有助于你更好的理解本文的思想。

# 本质不同

## 递推顺讯

在线性动态规划中，我们在 dp 表中递推顺讯为按行按列递推。在一维输入，递推顺序为。

![1D demo](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/interval_dp/1d_recurrence_demo.png)

在二维输入中，递推顺讯为

![2d demo](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/interval_dp/2d_recurrence_demo.png)

## 区间 dp

在区间 dp 中，往往我们递推一个二维的 dp 表格。而我们递推原则是从小的区间递推至大的区间，最终的答案存储在表示整个区间的状态中,例如`f[1][N]`位置。

![区间dp图示](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/interval_dp/interval_dp_demo.png)

# 例题 石子合并

**试一试**

- [石子合并](https://geniuscode.tech/problem/%E7%AE%97%E6%B3%95%E5%9F%BA%E7%A1%80-%E5%8A%A8%E6%80%81%E8%A7%84%E5%88%92-%E7%9F%B3%E5%AD%90%E5%90%88%E5%B9%B6)

## 状态表示

`int f[N][N]` , `f[i][j]` 表示合并区间`[i , j]`内所有石子的最小代价。

## 初始化

- 因为求取的是最小值，将整个`f`数字初始化为`INF`。
- 将 `f[i][i]` 初始化`0`,因为合并一堆石子不需代价。

## 递推

### 顺讯

枚举所有的区间长度，从长度为 `2` 开始 , 到长度为 `n`结束 。再枚举所有的起点，以真的得到这些区间。

对于一个新的位置 `f[i][j]` , 考虑其最后一次合并的情况。换言之，考虑将这堆石子分成左右两份会有哪些情况。显然，共有 `j - i` 中情况，其可能分割的点数量为区间长度减一。

![分割石子](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/interval_dp/stones_split.png)

### 递推式

因为所有更小的区间已经有解，而合并任意`stones[i][ki]` 和 `stones[ki+1][j]`的代价都是固定的，因为合并前是左右两堆，所以任意一种**分割方式的合并代价都是左边区间的石子数量+右边区间的石子数量**，也即是这堆石子的总数量，`sum(stones[i] , stones[j])`。

所以`f[i][j]` 求解时选择 `f[i][ki] + f[ki+1][j]`最小的哪个即可。

```c++
f[i][j] = min(f[i][j] , f[i][ki] + f[ki+1][j] + sum(stones[i] , stones[j]));
```

## 答案

答案在`f[1][n]`位置，表示合并石子区间`[1 , n]`的最小代价。

## 完整代码

```c++
#include<iostream>
#include<cstring>
using namespace std;

const int N = 310;
int stones[N] , presum[N] , f[N][N];

int main()
{
    int n; cin >> n;
    for(int i = 1 ; i <= n ; i++)
    {
        cin >> stones[i];
        presum[i] = stones[i] + presum[i-1];
    }

    memset(f , 0x3f , sizeof f);

    for(int i = 1 ; i <= n ; i++) f[i][i] = 0;

    for(int len = 2 ; len <= n ; len++)
    {
        for(int start = 1 ; start + len - 1 <= n ; start++)
        {
            int end = start + len - 1;
            for(int k = start ; k <= end - 1  ; k++)
            {
                f[start][end] = min(f[start][end] , f[start][k] + f[k+1][end] + presum[end] - presum[start-1]);
            }
        }
    }

    cout << f[1][n];
}
```
