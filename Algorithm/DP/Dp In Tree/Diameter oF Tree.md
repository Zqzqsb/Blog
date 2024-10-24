---
title: Diameter oF Tree
tags:
  - 算法
  - 动态规划
  - 树形DP
createTime: 2024-10-23
author: ZQ
permalink: /algorithm/dp/tree/Diameter/
---

本文讲解了如何求解的树的直径问题。

<!-- more -->

## 问题定义

+ 路径：一棵树上，任意两个节点之间最多有一条简单路径。
+ 直径：一棵树上，最长的路径为树的直径

## 无权树的直径

###  边缘点更远

当我们从无权树的任意节点出发执行`DFS`（或`BFS`）时，路径不断向树的深处探索。离起始点最远的那个节点必然在树的最外围，即“树的边缘”，因为在一个树形结构中，边缘节点（叶子节点）是距离其他部分最远的节点之一。

### 找到直径端点

从任意一个节点 `u` 开始执行`DFS`，找到了最远的节点 `v`。`v`必定在树的直径上。

**反证证明**  假设从 `u` 出发找到的最远节点`v` 不是树直径的端点。

+ 情况一 `u - v`的路径和树的一般直径`a - b`没有交点
	+ 因为树是联通的可以在 `u - v` 和 `a - b`上分别确定点 `x y`, `x y`之间存在一条一般路径
	+ 因为`v`是搜索到的最远路径 所以 
		+ 路径1  >= 路径2 + 路径3
		+ 路径1 - 路径2 >= 路径3
		+ 路径1 + 路径2 >= 路径3
	+ 这就与 `a - b`是树的一般直径矛盾了
+ 情况二 `u - v`的路径和树的一般直径`a - b`有交点
	+ 这种情况更为简单 可以类比情况一推出矛盾

![情况一](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/Diameter%20Of%20Tree/%E7%A4%BA%E4%BE%8B%E4%B8%80.png)

### 求解算法

1. 从任一点出发，使用`BFS` , 找到树的直径的端点。
2. 从树的端点出发，使用`BFS`,找出树的直径


## 带权树

### 树形DP

1. 从任一节点出发，将次节点视为根(最上层节点)。
2. 对于每个节点，再`DFS`中求出这个节点往叶节点方向能走出的最长路径。
3. 在这个过程中可以统计出经过该节点的最长路径。
	+ 最长路径是 所有往下的路径中选择最大和次大的两条组合而成

> 因为路径中可以只包含一个点， 所以置换的初始距离都为零。

![示意图](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/Diameter%20Of%20Tree/Dp%E6%8E%A8%E5%AF%BC.png)

### 例题

> [Acwing1072. 树的最长路径](https://www.acwing.com/problem/content/1074/)

```cpp
#include<iostream>
#include<cstring>
using namespace std;

const int N = 2e4 + 10;
int h[N] , e[N] , ne[N] , w[N] , idx;
int ans = 0; // 因为路径中可以只包含一个点 所以最短路径的长度为0 

void init() 
{
    memset(h , -1 , sizeof h);
}

void add(int a , int b , int c) 
{
    w[idx] = c , e[idx] = b , ne[idx] = h[a] , h[a] = idx++;
}

// 返回u 往下到直到叶节点的一条最长路径
int dfs(int u , int f)
{
    int res = 0;
    int m1 = 0  , m2 = 0; 
    for(int i = h[u] ; i != -1 ; i = ne[i])
    {
        int j = e[i];
        
        if(j == f) continue;
        
        int route = dfs(j , u) + w[i];
        res = max(res , route);
        
        if(route >= m1) m2 = m1 , m1 = route;
        else if(route > m2) m2 = route;
    }
    
    ans = max(ans , m1 + m2);
    return res;
}

int main() 
{
    init();
    
    int n; cin >> n;
    
    int a , b , c;
    for(int i = 1 ; i < n ; i++)
    {
        cin >> a >> b >> c;
        add(a , b , c); add(b , a  , c);
    }
    
    // 从任一节点 拎起这棵树
    // 在这个过程遍历每个节点 并且考量经过每个节点的所有路径
    // 因为每个节点只有唯一的入口 所以这个过程是 O(N) 的。
    dfs(1 , -1);
    
    cout << ans;
}
```