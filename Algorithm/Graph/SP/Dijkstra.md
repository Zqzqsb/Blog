---
title: Dijkstra
categories:
  - 算法
tags:
  - 图论
  - 最短路
createTime: 2024-9-8
permalink: /algorithm/graph/Dijkstra/
---

本文给出了`Dijkstra`的朴素写法，堆优化写法，算法细节和复杂度分析，已经对于该算法的正确性证明。文章的题目使用了`Acwing`的模板题。

<!-- more -->

## 算法简介

`Dijsktra`工作在**不含负权边的图**中，其会维护一个已访问集合(子图)，所有在已访问集合中的节点都有一个到源点的最小路径值。算法一般迭代`N`次，`N`是图中节点的规模，每轮迭代中，会从未访问子图找到一个节点置入访问集合中，这个节点是到未访问子图中到源点距离最近的集合，当这个节点被**纳入**访问集合之后， 它会更新其他未访问节点的距离。

+ 第一次访问即确定最短路径值，所以当第一次访问到终点可以结束迭代轮次
+ 源点和终点位于不同联通分量时，算法不一定在迭代轮次找到下一个节点执行纳入操作

## 朴素写法

在邻接矩阵实现其朴素写法，[acwing849](https://www.acwing.com/problem/content/description/851/)

```cpp
#include<iostream>
#include<cstring>
using namespace std;

const int N = 510;
int graph[N][N];
int dis[N] , vis[N];

void init()
{
    memset(dis , 0x3f , sizeof dis); # 初始时, 源点到其他点的距离都为无穷大
    memset(graph , 0x3f , sizeof graph);
}

void add(int a , int b , int c)
{
    graph[a][b] = min(graph[a][b] , c); # 在存储边时进行去重，保留更短的边
}

void dijsktra(int start , int end , int num_nodes)
{
    dis[start] = 0;

	# 迭代轮次
    for(int t = 1 ; t <= num_nodes ; t++)
    {
	    # 找到一个 未访问的 距离最小点
        int min_node = 0;
        for(int i = 1 ; i <= num_nodes ; i++)
        {
            if(!vis[i] && dis[i] < dis[min_node])
                min_node = i;
        }
        
        if(min_node == 0) return; # 没找到 停止
        if(min_node == end)  return; # 找到终点 停止
        vis[min_node] = true; # 纳入

		# 更新其他未访问节点的距离
        for(int i = 1 ; i <= num_nodes ; i++)
        {
            if(!vis[i] && dis[i] > dis[min_node] + graph[min_node][i])
            {
                dis[i] = dis[min_node] + graph[min_node][i]; 
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
        int a , b , c; scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    dijsktra(1 ,  n , n);
    if(dis[n] == 0x3f3f3f3f) cout << -1;
    else cout << dis[n];
}
```

### 复杂度

+ 时间复杂度 `O(n^2)`，每次**纳入**操作需要遍历所有节点，纳入操作需要做`n`次。
+ 空间复杂度取决于建图结构。

## 堆优化

使用堆来加速最近节点查找的过程，将所有的节点放入堆中，堆顶是距离已记录结构最近的节点。

### 代码

使用邻接表实现其代码，[acwing850](https://www.acwing.com/problem/content/description/852/)

```cpp
#include<iostream>
#include<queue>
#include<cstring>
#include<vector>
using namespace std;

const int N = 2e5;
int h[N] , e[N] , w[N] , ne[N] , idx;
int vis[N] , dis[N];
typedef pair<int, int> pos;

void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
} 

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a]; h[a] = idx++;
}

void dijkstra(int start , int end , int num_nodes)
{
	// 将起点放入优先队列
    priority_queue<pos , vector<pos> , greater<pos>> q;
    q.push({0 , start}); dis[start] = 0;
    
    // 被更新的节点会加入优先队列
    while(q.size())
    {
	    // 弹出队头 队头即当前距离最小的未被记录的点
        int node = q.top().second;
        q.pop(); 
        
	    // 因为一个节点可能被多个其他更新距离，队列中可能一个节点的多个距离
	    // 最小的距离会被首先弹出并且记录，其他距离不需要记录。
        if(vis[node]) continue; 
        // 如果记录到终点可以直接返回
        if(node == end) return;

		// 纳入这个点
        vis[node] = true;
		// 更新其他点的距离 如果其他点的距离被更新 那加入堆中
        for(int i = h[node] ; i != -1 ; i = ne[i])
        {
            int j = e[i];
            if(vis[j]) continue;
            if(dis[j] > dis[node] + w[i])
            {
                dis[j] = dis[node] + w[i];
                q.push({dis[j] , j});
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
        int a , b , c; scanf("%d %d %d" , &a , &b , &c);
        add(a , b , c);
    }
    
    dijkstra(1 , n , n);
    
    if(dis[n] == 0x3f3f3f3f) cout << -1 << endl;
    else cout << dis[n];
}
```

### 复杂度

+  时间复杂度 `O(nlogn)` , 每次调整堆的时间复杂度是`O(logn)`
+  建堆的空间复杂度 ，最坏情况为`O(n^2)`,实际运行会小于`O(n)`

## `Dijkstra`的证明

> 定理: 最短路径的子路径仍然是最短路径(反证易得)

要证明: `Dijsktra`中，将定点`u`添加到已记录集合`S = {1...x}`中时，`dist[u] = real[u]`。

证明: 
+ 假设待证定理不成立，可得 将`u`加入集合中时，`dist[u] > real[u]` , 则存在一条真实最短路，不妨设其为`<1....x y....u>` 其中边`(x , y)`横跨 `<S , V-S>` , `x`属于`S` , `y`属于`V-S`,对于任意`x` 属于 `S`, 有 `rel[x] = dist[x]`。
+ `<1...x y>` 是 `<1...x y...u>`的子路径，故
	+ `real[y]` = `rel[x] + w[x][y]` = `dist[x] + w[x][y]`
+ 算法对从`x`出发的所有边进行松弛操作，故
	+ `dist[y]` <= `dist[y] + w[x][y]` = `real[y]`
+ 观察路径`<1...x y...u>`
	+ `dist[u]` > `real[u]` >= `real[y]` = `dist[y]`
+ 由于`dist[u]` > `dist[y]` 所以`u`不可能下一个被添加，矛盾。



