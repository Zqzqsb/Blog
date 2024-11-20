---
title: Topological Sort
categories:
  - 算法
tags:
  - 图论
  - Tpsort
createTime: 2024-9-29
permalink: /algorithm/graph/tpsort/
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/TpSort/cover.png
---
![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/TpSort/cover.png)
本文讲解了拓扑的排序的一般实现方法和它在`AOV`和`AOE`网络中的应用。

<!-- more -->

## AOV 网

日常生活中，一项工程都可以看作是由若干个子工程组成的集合，这些子工程之间必定存在一定的先后顺序，即某些子工程必须在其他的一些子工程完成后才能开始。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/TpSort/AOV.png)

我们用有向图来表现子工程之间的先后关系，子工程之间的先后关系为有向边，这种有向图称为顶点活动网络，即 AOV 网 (Activity On Vertex Network)。一个 AOV 网必定是一个 DAG，即不带有回路。在 AOV 网中，顶点表示活动，弧(边)表示活动间的优先关系。

拓扑排序也可以解释为将 AOV 网中所有活动排成一个序列，使得每个活动的前驱活动都排在该活动的前面（一个 AOV 网中的拓扑排序也不是唯一的。

## 拓扑排序

### 流程

+ 在建图的过程中统计所有边的入度
+ 找到没有入度的节点入队
+ 记录并弹出队头，减少其他节点入度
	+ 如果有节点的入度减少为零，那么将它入队
+ 重复执行，直到队列空

如果弹出的节点数量等于图中所有节点的数量，那么该图存在一个拓扑序列。

### 代码实现

```cpp
const int N = 1e5 + 10;
int h[N] , e[N] , ne[N] , idx;
int IN[N];
vector<int> route;

void add(int a , int b)
{
    e[idx] = b; ne[idx] = h[a]; h[a] = idx++;
}

void TpSort(int n)
{
    queue<int> q;

	// 寻找所有可能的入口 这些入口可以存在于图的多个联通分量中
    for(int i = 1 ; i <= n ; i++)
    {
        if(IN[i] == 0) q.push(i);
    }
    
    while(q.size())
    {
        int f = q.front(); q.pop(); route.push_back(f);
        for(int i = h[f] ; i != -1 ; i = ne[i])
        {
            int j = e[i]; IN[j]--;
            // 只有在入度减少时，新的入口才可能出现
            if(IN[j] == 0)
                q.push(j);
        }
    }

	// 判别序列是否包含所有节点
    if((int)route.size() < n) {cout << -1; return;}
    for(auto i : route) cout << i << " ";
}
```

## AOE网

与 AOV 网对应的是 AOE 网（Activity On Edge Network) 即边表示活动的网。

AOE 网是一个带权的有向无环图，其中顶点表示事件，弧表示活动持续的时间。通常，AOE 网可以用来估算工程的完成时间。AOE 网是无环的，且存在唯一入度为零的起始顶点（源点），以及唯一出度为零的完成顶点（汇点）。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/TpSort/AOE.png)


### 相关概念

+ 活动：AOE 网中，弧表示活动。弧的权值表示活动持续的时间，活动在事件被触发后开始。
+ 事件：AOE 网中，顶点表示事件，事件能被触发。
+ 弧(活动) 的最早开始时间：初始点到该弧起点的最长路径长度，记为 **earliest(e)**。
	+ 最长路径代表该节点的入度为零的最早时刻
+ 弧(活动) 的最迟开始时间：在不推迟整个工期的前提下，工程达到弧起点所表示的状态最晚能容忍的时间，记为 **latest(e)**。

### 关键路径

AOE 网中的有些活动是可以并行进行的，所以完成整个工程的最短时间是从源点到汇点的最长活动路径长度（路径长度是指路径上各活动的持续时间之和，即弧的权值之和）。因为一项工程需要完成所有工程内的活动，所以最长的活动路径即是关键路径，它决定工程完成的总时间。

d(i) = l(i) − e(i)，即活动最迟开始时间与最早开始时间的差额，这代表着活动可以拖延的时间。如果一个活动的时间余量为 0，就意味着该活动不能拖延时间，称为 关键活动，必须立即完成，否则就将拖延整个工期。
而时间余量为 0 的所有边连起来，就是关键路径了。
要求时间余量 d, 就要先求活动的最早开始时间 e 和最迟开始时间 l，要求 e 和 l 就要先求事件最早发生时间 ve 和最迟发生时间 vl。


```cpp
#include<bits/stdc++.h>
#define N 100010
using namespace std;
struct edge {
    int to, w;
}; 
vector <edge> g[N]; // 邻接表
int indgr[N], topo[N], n, m; 
int ve[N], e[N], vl[N];
bool topoSort() {
    queue <int> q;
    int k = 0; 
    for(int i = 1; i <= n; i++)
        if(indgr[i] == 0) q.push(i); 
    while(!q.empty()) {
        int u = q.front(); q.pop();
        topo[++k] = u; // 记录拓扑序列
        for(int i = 0; i < g[u].size(); i++) {
            int v = g[u][i].to;
            if(--indgr[v]==0) q.push(v); 
        } 
    }
    if(k < n) return 0; 
    return 1; 
}

void build_ve() { // 计算事件每个节点的最晚到达时间(节点的每条出边的最早发生时间)
    for(int i = 1; i <= n; i++) ve[i]=0; 
    	
    for(int j = 1; j <= n; j++) {
        int u = topo[j]; 
        // 按拓扑遍历所有出边 更新边对象节点的最晚到达时间(取)
        // 这个过程可以在拓扑排序过程中同步发生
        for(int i = 0; i < g[u].size(); i++) {
            int v = g[u][i].to, w = g[u][i].w;
            ve[v] = max(ve[v], ve[u] + w);
        }
    } 
}
void build_vl() { // 计算事件最迟发生时间

	// 活动的最早发生事件 = 边的最早开始时间 = 顶点最晚到达时间
    for(int i = 1; i <= n; i++) vl[i] = ve[n]; 

    for(int j = n-1; j >= 1; j--) {
        int u = topo[j]; 
	    // 按逆拓扑序 对于节点的所有后置节点
		// 当前节点的最晚到达时间 (只有这个节点到达了，这个节点的出边才能开始)
		// 是后置节点的最晚到达时间 - 活动的时间 中最早的时间
        for(int i = 0; i < g[u].size(); ++i){
            int v = g[u][i].to, w = g[u][i].w;
            vl[u] = min(vl[u], vl[v] - w);
        }
    }
}


int main() {
    cin >> n >> m; // n 个事件，m 个活动
    for(int i = 0; i < m; i++){
        int u, v, w;
        cin >> u >> v >> w;
        g[u].push_back((edge){v,w}); 
        indgr[v]++; // 记录入度 
    } 
    if(topoSort()) { // 拓扑排序成功
        for(int i = 1; i <= n; i++) {
            cout << topo[i] << " "; 
        }
        cout << endl;
        build_ve();
        build_vl();
        critical();
    }
    else {
        cout << -1 << endl;
    }
    return 0;
}
```

### 测试样例

```txt
样例1:
6 8
1 2 3
1 3 2
2 4 2
2 5 3
3 4 4
3 6 3
4 6 2
5 6 1

输出1:
1 2 3 5 4 6 
<1,3>
<3,4>
<4,6>

样例2:
8 12
1 2 6
1 3 7
2 4 3
2 5 5
3 5 4
4 6 2
4 8 5
5 4 3
5 6 4
5 7 3
6 8 2
7 8 4

输出2:
1 2 3 5 4 7 6 8 
<1,2>
<2,5>
<5,4>
<4,8>
19


```
