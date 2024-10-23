---
title: Dp In Tree
tags:
  - 算法
  - 动态规划
  - 树形DP
createTime: 2024-10-23
author: ZQ
permalink: /algorithm/dp/tree/concept/
---

本文讲解了树形`dp`的一些概念和一个典型例题。

<!-- more -->

## 概述

树形DP（树形动态规划）是一种应用于树形结构（如树或有向无环图）的动态规划算法。其核心思想是通过递归的方式处理树的节点，逐步从树的叶子节点向根节点传递信息，从而在根节点得到最终结果。它广泛应用于图论中的路径问题、树的最优划分问题等。

树形DP的得核心是在`DFS`退栈时进行递推计算，推导顺序是其核心

## 基本步骤

1. **确定状态**：每个节点的状态通常与其子树的结构有关。我们需要明确对于每个节点的不同状态（如节点值、路径长度等），如何表示子问题的解。
2. **状态转移**：通过节点的状态来确定父节点的状态，通常通过遍历节点的子节点，将子节点的状态转移到父节点。这一步就是动态规划中的“递推”过程。
3. **递归处理**：一般使用深度优先搜索（DFS）进行递归，从叶子节点到根节点，计算出每个节点的状态值。
4. **初始条件**：叶子节点的状态通常是已知的，因为它们没有子节点，不需要状态转移。

## 常见应用

1. **树的最长路径问题**：找到树中两点之间的最长路径。可以通过递归计算每个节点为起点的最长路径，然后更新全局最长路径。
2. **树的直径问题**：即找出树中两点之间的最长距离。可以通过动态规划计算每个节点的最长上行路径和下行路径，最终合成得到树的直径。
3. **节点的权值选择问题**：有些问题要求我们选择树中部分节点的权值，比如在没有相邻节点的情况下，选取最大权值的节点集合。可以通过树形DP设计状态，判断是否选择当前节点，再递归到子节点来做选择。

## 例题 

> [Acwing285](https://www.acwing.com/problem/content/287/) 没有上司的舞会

### 实现

```cpp
#include<iostream>
#include<cstring>
using namespace std;

const int N = 1e4;
int h[N] , e[N] , ne[N] , idx;
int happy[N] , dp[N][2] , fa[N];

void init()
{
    memset(h , -1 , sizeof h);
}

void add(int a , int b)
{
    e[idx] = b; ne[idx] = h[a] ; h[a] = idx++;
}

void dfs(int u)
{

    dp[u][1] = happy[u];
    
    for(int i = h[u] ; i != -1 ; i = ne[i])
    {
        int j = e[i];

		// 先进行DFS搜索
        dfs(j);
        
        // 选择当前的节点 就只能考虑儿子都不选的情况的快乐值
        dp[u][1] += dp[j][0]; 
        
        // 不选当前节点 可以在任一儿子选或不选的答案中取大的那个
        dp[u][0] += max(dp[j][1] , dp[j][0]);
    }
    
} 


int main()
{
    init();
    
    int n; cin >> n;
    
    for(int i = 1 ; i <= n ; i++)
        cin >> happy[i];
    
    for(int i = 1 ; i < n ; i++)
    {
        int a , b;
        cin >> a >> b;
        add(b , a);
        fa[a] ++;
    }
    
    int root = -1;
    for(int i = 1 ; i <= n ; i++)
    {
        if(fa[i] == 0)
        {
            root = i;
            break;
        }
    }
    
    dfs(root);
    cout << max(dp[root][0] , dp[root][1]);
}
```
