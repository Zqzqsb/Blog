---
title: Minimum Spanning Tree
categories:
  - 算法
tags:
  - 图论
  - MST
createTime: 2024-9-27
permalink: /algorithm/graph/mst/
---

本文讲解了图的最小生成树问题以及两个相关的求解算法,`Prim`算法和`kruskal`算法。

<!--more-->

## 问题概述

最小生成树（MST）问题是指在一个加权无向图中，找到一棵生成树，使得树中所有边的权值之和最小。最小生成树在网络设计、路由优化等领域有重要应用。

## `Prim`算法

### 算法过程

1. 从任意一个顶点开始，将其加入生成树。
2. 选取与生成树相连的边中权值最小的边，将对应顶点加入生成树。
3. 重复步骤2，直到所有顶点都在生成树中。

### 算法实现

> [Acwing 858](https://www.acwing.com/problem/content/description/860/)

**朴素实现**

+ 算法效率`0(V^2)`

```cpp
#include<iostream>
#include<cstring>
using namespace std;

const int N = 510;
int graph[N][N];
int tree[N] , dis[N];

void init()
{
    // 将所有节点设为不可达
    memset(graph , 0x3f , sizeof graph);
    memset(dis  , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    graph[a][b] = min(graph[a][b] , c);
    graph[b][a] = graph[a][b];
}

void Prim(int n)
{
    dis[1] = 0; // 设置一个起始节点
    int res = 0;
    
    // 遍历所有节点 进行n次
    for(int t = 1 ; t <= n ; t++)
    {
        int min_node = 0;
        for(int i = 1 ; i <= n ; i++)
        {
            // 找一个不在书中且距离最小的节点
            if(!tree[i] && dis[i] < dis[min_node])
                min_node = i;
        }
        
        // 如果图是完全连通的 那么每次都应该找到一个新的节点
        if(min_node == 0)
        {
            cout << "impossible";
            return;
        }
        
        // 将这个节点加入生成树 并更新其他节点的距离
        res += dis[min_node]; tree[min_node] = true;
        
        for(int i = 1 ; i <= n ; i++)
        {
            if(!tree[i]) dis[i] = min(dis[i] , graph[min_node][i]);
        }
        
    }
    
    cout << res;
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
    
    Prim(n);
}
```

**堆优化实现**

+ 算法效率`O(VE)` 。

```cpp
#include<iostream>
#include<cstring>
#include<queue>
#include<utility>
#include<vector>
using namespace std;

const int N = 510  , M = 2e5 + 10;
int h[N] , e[M] , w[M] , ne[M] , idx;
int inTree[N] , dis[N];
typedef pair<int , int> POS;
void init()
{
    memset(h , -1 , sizeof h);
    memset(dis , 0x3f , sizeof dis);
}

void add(int a , int b , int c)
{
    e[idx] = b; w[idx] = c; ne[idx] = h[a]; h[a] = idx++;
}

void Prim(int n)
{
    priority_queue<POS , vector<POS> , greater<POS> > heap;
    heap.push(POS(0 , 1)); dis[1] = 0;
    int res = 0 , cnt = 0;
    while(heap.size())
    {
        // 取出堆顶的元素
        int node = heap.top().second; heap.pop();
       
        // 堆中会加入重复的元素 如果第一次拿到的是有效的最短距离 后面的重复记录则跳过
        if(inTree[node]) continue;
        
        // 将有效的节点数量加一 并将这个距离加入生成树
        cnt++; res += dis[node]; inTree[node] = 1;
        
        // 根据堆顶元素更新其他元素的可达距离
        for(int i = h[node] ; i != -1 ; i = ne[i])
        {
            int j = e[i]; 
            // 将不在树中 切距离变小的节点加入堆
            if(!inTree[j] && dis[j] > w[i])
            {
                dis[j] = w[i];
                heap.push(POS(dis[j] , j));
            }
        }

    }

    if(cnt == n) cout << res;
    else cout << "impossible" << endl;
}

int main()
{
    init();
    
    int n , m;
    cin >> n >> m;
    int a , b , w;
    while(m--)
    {
        scanf("%d %d %d" , &a , &b , &w);
        add(a , b , w); add(b , a , w);   
    }

    Prim(n);
}
```


## `kruskal`算法

### 算法过程

1. 将所有边按权重排序。
2. 从最小边开始，依次检查每条边，若加入生成树不形成环，则加入。
3. 重复步骤2，直到生成树包含 `V-1` 条边( `V`为顶点数）。

### 并查集实现

> [Acwing 859](https://www.acwing.com/problem/content/description/861/)

+ 算法效率`O(ElogE)`(排序，并查集操作的效率接近`O(E)`

> **并查集操作**：在算法中需要多次进行查找和合并操作，这些操作的时间复杂度为 O(α(V))，其中 V 是顶点的数量，α 是阿克曼函数的逆（增长非常缓慢，可以视为常数）。

```cpp
#include<iostream>
#include<algorithm>
using namespace std;

const int N = 1e5 + 10;
struct Edge
{
    int a, b ,c;
    bool operator<(const Edge &e1)
    {
        return this -> c < e1.c;
    }
}edges[N*2];

int fa[N];

void init()
{
    for(int i = 0 ; i < N ; i++)
    {
        fa[i] = i;
    }
}

int find(int x)
{
    if(fa[x] != x) fa[x] = find(fa[x]);
    return fa[x];
}

void merge(int x , int y)
{
    int fx = find(x) , fy = find(y);
    fa[fy] = fx;
}

void kruskal(int num_nodes , int num_edges)
{
    sort(edges , edges+num_edges);
    int cnt = 0 , res = 0;
    for(int i = 0 ; i < num_edges ; i++)
    {
        Edge e = edges[i];
        if(find(e.a) != find(e.b))
        {
            merge(e.a , e.b);
            cnt++; res += e.c;
        }
        if(cnt == num_nodes) break;
    }
    
    // mst的边数是节点数减一
    if(cnt == num_nodes-1) cout << res;
    else cout << "impossible";
}

int main()
{
    init();
    
    int n , m; cin >> n >> m;
    for(int i = 0 ; i < m ; i++)
    {
        scanf("%d %d %d" , &edges[i].a , &edges[i].b , &edges[i].c);
    }
    kruskal(n , m);
}
```