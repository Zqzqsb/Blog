---
title: Bellman-Ford
categories:
  - 算法
tags:
  - 图论
  - 最短路
createTime: 2024-9-10
permalink: /algorithm/graph/bellmanford/
---

`Bellman-Ford`如何处理有边数限制的最短路,以及它和款搜的比较。

<!-- more -->

## 概述

`Bellman-Ford`在有边数限制的条件下求解出最短路径。使用`BFS`的方式向外更新，可以计算通过负环并且有一定边数限制的最短路。

`Bellman-Ford`算法适合工作在含有负权边的稀疏图中。

简单描述其算法过程
+ 做`k`轮迭代，每轮迭代遍历所有边。
+ 每当遍历到一条边时，用这条有向边更新有向边指向的那个节点。

在算法执行的过程中，某些负权边会导致算法在`BFS`范围外进行更新。

## 实现

[Acwing 853](https://www.acwing.com/problem/content/description/855/)  

> 100ms

```cpp
#include <iostream>
#include <cstring>
using namespace std;

const int M = 1e5 + 10 , N = 510;
struct Edge 
{
    int a , b , c;
}edges[M];

int dis[N] , last[N];

void init()
{
    memset(dis , 0x3f , sizeof dis);
}

void bellmanford(int start , int m , int k)
{
    dis[start] = 0;
    for(int t = 1 ; t <= k ; t++)
    {
	    // 为了放置在一个轮次传递更新，使用上一轮次的距离更新下一轮次
        memcpy(last , dis , sizeof dis);
        for(int i = 1 ; i <= m ; i++)
        {
            Edge e = edges[i]; 
            dis[e.b] = min(dis[e.b] , last[e.a] + e.c);
        }
    }
}

int main()
{
    init();
    int n , m , k; cin >> n >> m >> k;
    
    for(int i = 1 ; i <= m ; i++)
    {
        int a , b , c; scanf("%d %d %d" , &a , &b , &c);
        edges[i] = {a , b , c};
    }

    bellmanford(1, m , k);
    
    if(dis[n] > 0x3f3f3f3f / 2) cout << "impossible";
    else cout << dis[n];
}
```

###  与`BFS`比较

> 150ms

```cpp
#include<iostream>
#include<cstring>
#include<queue>

using namespace std;

const int N = 510 , M = 1e5 + 10;
int h[M] , e[M] , w[M] , ne[M] , idx;
int dis[N] , last[N] , st[N];

void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a]; h[a] = idx++;
}

void bfs(int start , int num_nodes , int k)
{
    queue<int> q; q.push(start); dis[start] = 0;
    int num = 1;
    
    while(k--)
    {
        int num_level = num; num = 0;
        
        memcpy(last , dis , sizeof dis);
        // st数组控制节点在一个更新波次中只会入队一次
        // 认识到 节点会在一个更新波次中被多个其他节点更新距离
        memset(st , 0 , sizeof st);
        while(num_level--)
        {
            int f = q.front(); q.pop();
            
            for(int i = h[f] ; i != -1 ; i = ne[i])
            {
                int j = e[i];
                if(dis[j] > last[f] + w[i])
                {
                    dis[j] = last[f] + w[i];
                    if(!st[j])
                    {
                        q.push(j); num++;
                        st[j] = true;
                    }
                }
            }
        }
    }
}

int main()
{
    init();
    int n , m , k; cin >> n >> m >> k;
    while(m--)
    {
        int a , b , c; scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    
    bfs(1 , n , k);
    if(dis[n] == 0x3f3f3f3f) cout << "impossible";
    else cout << dis[n];
}
```

+ 在例题的图中作业时，`bellman-ford`和`BFS`有大致相当的效率
+ 可以详见`bellman-ford`适用于边数较少的情况, `BFS`适用于边数较多，迭代轮次较少的场景。

### 检测负环路

如果`Bellman-Ford`的迭代次数超过了图中的节点个数，那么就出现了负环路。因为在不含负环路的图中，任何一条距离更新路径不会超过图中节点的数目。

[Acwing 852](https://www.acwing.com/problem/content/description/854/)

> 600ms

```cpp

```

