---
title: Floyd-Warshall
tags:
  - 最短路
  - 图论
createTime: 2024-9-20
permalink: /algorithm/graph/floyd/
---

笔记讲解了`floyd`的算法原理和实现。

<!-- more -->

## 概述

`Floyd-Warshall` 算法的正确性依赖于 **动态规划** 和 **递推** 原理。它通过逐步增加中间节点，保证每一对顶点之间的最短路径逐步逼近最终的最短路径。算法的核心思想是，如果从顶点 `i` 到顶点 `j` 经过某个中间顶点 `k`，那么从 `i` 到 `j` 的最短路径长度要么保持原值，要么通过 `k` 使得路径变短。

## 归纳证明

通过数学归纳法来证明：

- **归纳基**：当没有任何中间节点时，`dist[i][j]` 初始化为图中已有的路径长度或者无穷大。这是正确的初始状态。
- **归纳假设**：假设在前 `k-1` 个中间节点被考虑之后，`dist[i][j]` 已经是从 `i` 到 `j` 的最短路径，且经过的所有中间节点都是从集合 {1, 2, ..., k-1} 中选择的。
- **归纳步骤**：现在考虑将第 `k` 个节点作为可能的中间节点。根据递推公式，我们更新 `dist[i][j]`，如果经过 `k` 可以得到更短的路径，则更新为更短的路径。否则保持原值。这样，在 `k` 被加入考虑之后，`dist[i][j]` 是从 `i` 到 `j` 的最短路径，且可以经过的中间节点来自集合 {1, 2, ..., k}。

因此，当所有的节点都被依次作为中间节点考虑后，`dist[i][j]` 最终包含了从 `i` 到 `j` 的最短路径。

## 算法实现

[Acwing854](https://www.acwing.com/problem/content/856/)

```cpp
#include<iostream>
#include<cstring>

using namespace std;

const int N = 210;
int graph[N][N];

int main()
{
    memset(graph , 0x3f , sizeof graph);
    for(int i = 0 ; i < N ; i++)
    {
        graph[i][i] = 0;
    }
    
    int n , m , k; cin >> n >> m >> k;
    
    while(m--)
    {
        int a , b , c; scanf("%d %d %d\n" , &a , &b , &c);
        graph[a][b] = min(graph[a][b] , c);
    }
    
    for(int k = 1 ; k <= n ; k++)
        for(int i = 1 ; i <= n ; i++)
            for(int j = 1 ; j <= n ; j++)
                graph[i][j] = min(graph[i][j] , graph[i][k] + graph[k][j]);
                
    while(k--)
    {
        int a , b; scanf("%d %d\n", &a , &b);
        if(graph[a][b] > 0x3f3f3f3f / 2) cout << "impossible" << endl;
        else cout << graph[a][b] << endl;
    }
}
```

## 效率

`Floyd-Warshall`的时间复杂度为`O(n^3)`