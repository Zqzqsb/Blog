---
title: SPFA
tags:
  - 最短路
  - 图论
createTime: 2024-9-8
permalink: /algorithm/graph/spfa/
---

讲述了我对`SPFA`算法的理解,以及它的相关使用场景。

<!-- more -->

## 概述

`SPFA`（Shortest Path Faster Algorithm，最短路径加速算法）是用于解决单源最短路径问题的算法。它是Bellman-Ford算法的改进版，主要用于处理带有负权边的图。相比于Bellman-Ford算法，SPFA在很多情况下更快，虽然在最坏情况下时间复杂度仍为`O(VE)`，但在实际应用中通常能达到`O(E)`的效果，一般来说其效率和堆优化的`dijsktra`相近。

`SPFA`使用队列（通常是双端队列）来优化`Bellman-Ford`算法的松弛过程，它不再像`Bellman-Ford`那样每次都对所有边进行松弛，而是只对可能导致最短路径改变的顶点进行松弛。

可以记住在`spfa`实现中的一条核心思想，只有被更新距离的节点才有资格更新其他节点的距离，直到这个过程完成收敛，可以求出源点到其他所有点的最短距离。可以想见，`spfa`在负环处无法收敛，所以可以用该算法来检测负环是否存在。

## 代码实现

在邻接表中对算法过程进行实现，[Acwing851](https://www.acwing.com/problem/content/853/).

在一般的`spfa`过程中，使用队列或者栈不会影响算法的运行效率，因为我们都需要等到算法的收敛。

```cpp
#include<iostream>
#include<cstring>
#include<queue>
using namespace std;

const int N = 1e5 + 10;
int h[N] , e[N] , ne[N] , w[N] , idx;
int dis[N] , st[N];

void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a]; h[a] = idx++;
}

void spfa(int start)
{
	// 更新起点的距离 并且入队
	dis[start] = 0;
    queue<int> q; q.push(start);
    
    while(q.size())
    {
	    // 弹出队头
        int n = q.front(); q.pop();
        st[n] = false;

		// 用队头更新其他节点的距离
        for(int i = h[n] ; i != -1 ; i = ne[i])
        {
            int j = e[i];
			// 对于距离变小且不在队列中元素，需要入队
            if(dis[j] > dis[n] + w[i])
            {
                dis[j] = dis[n] + w[i];
                if(!st[j])
                {
                    st[j] = true;
                    q.push(j);
                }
            }
        }
    }
}

int main()
{
    init();
    int n , m; cin >> n >> m;
    while(m--)
    {
        int a , b ,c; scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    spfa(1);
    if(dis[n] == 0x3f3f3f3f) cout << "impossible" << endl;
    else cout << dis[n];
}
```

## 重建路径

+ 每当有节点的距离被更新，就覆盖更新这个节点的前置节点。
+ 可以根据节点的其他属性进行排序。

## 判断负环

[Acwing 852](https://www.acwing.com/problem/content/description/854/)

+ 当所有距离都置为无穷大时，负权边会导致其他节点距离的更新，而在负权回路中，节点被更新的次数将没有上线。
+ 这个负环处会成为一个**负权制造源**，源源不断的向外更新其他节点的距离。
+ 在不含负权回路的图中，任一节点的被更新路径长度不会超过`n` , 因为任意两个点的最短路径最多包含`n`个节点。

> 1500ms

```cpp
#include<iostream>
#include<cstring>
#include<queue>
#include<string>
using namespace std;

const int N = 1e5 + 10;

int h[N] , e[N] , ne[N] , w[N] , idx;
int dis[N] , count[N] , st[N];

void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a] , h[a] = idx++;
}

string spfa(int n)
{
    queue<int> q;

	// 将所有的节点入队，最初的更新会发生在负权边处
    for(int i = 1 ; i <= n ; i++)
    {
        q.push(i); st[i] = true;
    }
    
    while(q.size())
    {
        int f = q.front(); st[f] = false; q.pop();
        
        
        for(int i = h[f] ; i != -1 ; i = ne[i])
        {
            int j = e[i];
            if(dis[j] > dis[f] + w[i])
            {
                dis[j] = dis[f] + w[i];
                
                if(count[j] >= n)
                    return "Yes";
                    
                count[j] = max(count[j] , count[f] + 1); // 保留最长的一条更新路径 
                
                if(!st[j]) {
                    q.push(j); st[j] = true;
                }
            }
        }
    }
    
    return "No";
}

int main()
{
    init();
    int n , m; cin >> n >> m;
    int a , b , c; 
    while(m--)   
    {
        scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    
    cout << spfa(n);
}
```

## 局限和优化

+ 这种判断负环的方式适合在稠密图中工作，因为理论上来说负权制造源制造的负权会波及到整个图。
+ 使用队列本质上是一种广度搜索实现，使用栈处理这个过程会更快，因为我的搜索目的是尽可能快的找到一条长的负权传播路径， 而算法的性质已经帮我们确定了一些搜索的起点(负权边的源点)。广度搜索存储了太多无意义的传播过程。

> 200ms

```cpp
#include<iostream>
#include<cstring>
#include<stack>
#include<string>
using namespace std;

const int N = 1e5 + 10;

int h[N] , e[N] , ne[N] , w[N] , idx;
int dis[N] , count[N] , st[N];

void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a] , h[a] = idx++;
}

string spfa(int n)
{
    stack<int> q;
    
    for(int i = 1 ; i <= n ; i++)
    {
        q.push(i); st[i] = true;
    }
    
    while(q.size())
    {
        int f = q.top(); st[f] = false; q.pop();
        
        
        for(int i = h[f] ; i != -1 ; i = ne[i])
        {
            int j = e[i];
            if(dis[j] > dis[f] + w[i])
            {
                dis[j] = dis[f] + w[i];
            
                if(count[j] >= n)
                    return "Yes";
                    
                count[j] = max(count[j] , count[f] + 1); // 保留最长的一条更新路径 
                
                if(!st[j]) {
                    q.push(j); st[j] = true;
                }
            }
        }
    }
    
    return "No";
}

int main()
{
    init();
    int n , m; cin >> n >> m;
    int a , b , c; 
    while(m--)   
    {
        scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    
    cout << spfa(n);
}
```