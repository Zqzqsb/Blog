---
title: Heap
createTime: 2024-1-29
tags:
  - 堆
author: ZQ
permalink: /algorithm/ds/heap/
---

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Heap/heaps.png)

本文讲解了堆的概念和实现方法。

<!-- more -->

## 基本概念

堆是一种**完全二叉树**（Complete Binary Tree），它具有以下性质：

- **完全性**：除了最后一层外，所有层都是完全填满的，且最后一层的节点尽可能地靠左排列。
- **堆序性**（Heap Property）：在堆中，每个节点的值都满足特定的顺序关系。根据不同的顺序关系，堆可以分为两种类型：
    - **最大堆（Max Heap）**：每个节点的值都不小于其子节点的值。根节点是整个堆中的最大值。
    - **最小堆（Min Heap）**：每个节点的值都不大于其子节点的值。根节点是整个堆中的最小值。

## 堆的表示

堆通常使用数组来表示，因为完全二叉树的特性使得堆可以高效地映射到数组索引。对于一个数组表示的堆：

- **父节点与子节点的关系**：
    - 对于索引为 `i` 的节点(从`0`开始索引)：
        - 左子节点的索引为 `2i + 1`
        - 右子节点的索引为 `2i + 2`
        - 父节点的索引为 `(i - 1) / 2`（向下取整)

## 主要操作

### 1. 插入（Insert）

将一个新元素插入堆中：

- 将新元素添加到堆的末尾（保持完全性）。
- 通过“上浮”（Sift Up）操作，将新元素与其父节点比较，若违反堆序性，则交换位置，直到堆序性恢复。

### 2. 删除（Delete）

从堆中删除根节点（最大堆中的最大值或最小堆中的最小值）：

- 将堆的最后一个元素移到根节点的位置。
- 通过“下沉”（Sift Down）操作，将新根与其子节点比较，若违反堆序性，则与较大（最大堆）或较小（最小堆）的子节点交换，直到堆序性恢复。

### 3. 堆化（Heapify）

将一个无序的数组转换为堆的过程：

- 从最后一个非叶子节点开始，依次对每个节点执行“下沉”操作。
- 这种方法的时间复杂度为 O(n)。

## 实现

堆的底层数组从`1`开始索引。

```cpp
#include<iostream>
#include<algorithm>

using namespace std;

const int N = 1e5 + 10;
int n , m;
int h[N] , cnt;

void down(int u) {
    int t = u;
        
    // 这两个 if 会选择出 双亲和左右儿子中 小的那个节点
    if(u * 2 <= cnt && h[u*2] < h[t]) t = u * 2;
    if(u * 2 + 1 <= cnt && h[u*2 + 1] < h[t]) t = u * 2 + 1;
    
    // 如果某个儿子更小(或最小) 那么把双亲节点和该儿子的值互换 并且递归向下调整
    if(u != t) {
        swap(h[u] , h[t]);
        down(t);
    }
}

void up(int u) {
    // 如果父节点更大 就交换 迭代向上更新
    while(u / 2 && h[u] < h[u/2]) {
        swap(h[u] , h[u/2]);
        u >>= 1;
    }
}

void heapify(int n) {
    // 满二叉树 从最后一个非叶子节点开始建堆
    // 最后一个非叶子节点的位置 是 floor(n / 2)
	for(int i = n / 2 ; i ; i --) down(i);
}
int main() {
    int n , m; cin >> n >> m;
    for(int i = 1 ; i <= n ; i ++) cin >> h[i];
    cnt = n;

	heapify(n);
	
    // 得到 m 个最小元素
    while(m --) {
        // 弹出最小元素 并且将堆尾元素换到堆顶 向下调整得到新的最小值
        cout << h[1] << " ";
        h[1] = h[cnt --]; 
        down(1);
    }
}
```