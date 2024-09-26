---
title: Union Set Union
createTime: 2024-9-22
description: 本文讲解了并查集结构和实现方法。
author: ZQ
tags:
- DataStructure
- DSU
permalink: /algorithm/ds/unionset/
---
<br> 本文讲解了并查集结构和实现方法。
<!-- more -->
## 概述

并查集（Disjoint Set Union，简称 DSU），这是一种用于处理集合合并和查询的数据结构。它通常包含两个主要操作：查找（Find）和合并（Union）。这个数据结构在解决连通性问题时非常有用，比如判断图中节点是否连通，或者将一组元素分成不相交的集合。

### 查找

+ 查找一个节点的所在集合的代表节点。可以把集合内节点的结构想象为一颗多叉树，代表节点是多叉树的根节点。
+ 如果两个节点的代表节点相同，则这两个节点位于相同的集合中；反之，则他们位于不用的集合中。

### 合并

在并查集框架内，合并指的是将两个节点所在的集合合并为一个结合。

## 一般过程

### 初始化

将所有节点初始化为一个单独集合，并将这个节点的代表节点置为自己。

```cpp
const int N;
int fa[N]; // 标志每个集合的代表节点

void init()
{
	for(int i = 0 ; i < N ; i++) fa[i] = i; // 初始化为集合 每个集合的代表节点为自己
}
```

### 查找

**递归查找**

+ 找到代表节点后，在递归函数中传递结果。

```cpp
int find(int x)
{
	if(fa[x] != x) return find(fa[x]);
	return fa[x];
}
```

**路径压缩**

+ 在函数退栈的时候压缩路径，将递归路径中所有的节点置为根节点的直接儿子。

```cpp
int find(int x)
{
	if(fa[x] != x) fa[x] = find(fa[x]); 
	return fa[x]; 
}
```

### 合并

**初始化**

```cpp
int fa[N] , rk[N];
void init(int n)
{
	for(int i = 1 ; i <= n ; i++)
	{
		fa[i] = i; rk[i] = 1;
	}
}
```

**一般合并**

```cpp
void merge(int x , int y)
{
	// fa[b] = a; 这是错的 会导致节点为根的子树脱离原本的集合

	int fx = find(x) , fy = find(y);
	fa[fx] = fy; // 将x所在的集合合并到y所在的集合
}
```

**按秩合并**

+ 节点的秩 是节点所在树的高度
+ 同时使用按秩合并和路径压缩 会导致秩的记录有问题

```cpp
void merge(int x , int y)
{
	// 找到 x , y 所在节点的代表节点
	int fx = find(x) , fy = find(j);
	if(fx == fy) return; // 如果两个节点在一个集合 无需合并
	
	// 比较两个集合的秩 思路是 秩大的合并秩小的 
	if(rk[fx] <= rk[fy])
		fa[fx] = fy; // 如果两个集合的秩相等 那么合并后秩会增加
	else
		fa[fy] = fx; // x 的秩大于 y 这种情况不会增加秩

	// 如果两个集合的秩相等并且 fx 那么 fy 会合并 fx
	// 这是 fy 所代表的集合秩会增加
	if(rk[x] == rk[y])
		rk[y]++;
}
```

### 集合的其他属性

+ 可以维护集合的其他属性，比如集合中节点的数量等等。
