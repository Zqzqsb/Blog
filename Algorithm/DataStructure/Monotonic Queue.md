---
title: Monotonic Queue
createTime: 2024-10-29
tags:
  - 数据结构
  - 单调性
author: ZQ
permalink: /algorithm/ds/monotonic/queue/
---

本文讲解了单调队列以及其处理的问题。

<!-- more -->

## 概述

单调队列是一种特殊的队列结构，用来维护一个序列中元素的某种单调性，通常用于解决滑动窗口类的问题。单调队列分为**单调递增队列**和**单调递减队列**两种，分别维护队列中的元素按从小到大或从大到小的顺序排列。它的核心思想是：在每次插入新元素或删除元素时，通过维护单调性来保持所需的数据结构特性。


## 操作

1. **入队**：插入新元素时，根据队列的单调性，删除队列尾部所有比当前元素更小或更大的元素（取决于队列的递增或递减性），然后将新元素加入队尾。
2. **出队**：当队首元素不再属于当前的窗口范围时，将其从队首移出。
3. **查询极值**：由于单调性，队首元素就是当前窗口的极值（最大值或最小值）。

  

## 应用场景

单调队列在解决一些滑动窗口类问题时非常高效，比如：

• **滑动窗口最大值或最小值问题**：在给定一个数组和一个窗口大小  k ，求出每个窗口中的最大或最小值。通过单调队列维护窗口范围内的元素，始终保持极值在队首。
• **子数组和的最小值或最大值**：在某些动态规划问题中，单调队列可用于维护一个范围内的最优解。

## 例题1

> [Acwing 154滑动窗口](https://www.acwing.com/problem/content/description/156/)

### 解法1 

使用`stl`的`deque`，时间为 `600ms`。

```cpp
#include<iostream>
#include<deque>
using namespace std;

const int N = 1e6 + 10;
int array[N];

int main()
{
    int n , k; 
    cin >> n >> k;
    
    deque<int> dq;
    
    for(int i = 1 ; i <= n ; i++)
    {
        scanf("%d" , &array[i]);
    }
    
    // 求最小值 维护一个升序队列
    // 队头为最小值
    for(int i = 1 ; i <= n ; i++)
    {
        // 每次移动窗口的左端
        if(dq.size() && dq.front() < i - k + 1) dq.pop_front();
        
        // 入队一个新元素 在队尾保持队列的单调性
        // 弹出所有比队尾大的元素 更前更大的元素是没有用的
        while(dq.size() && array[dq.back()] >= array[i]) dq.pop_back();
        
        dq.push_back(i);
        
        if(i >= k) printf("%d " , array[dq.front()]);
    }
    
    puts("");
    
    dq.clear();
    
    // 求最大值时 维护一个降序队列
    // 队头为最大值
    for(int i = 1 ; i <= n ; i++)
    {
        // 每次移动窗口的左端
        if(dq.size() && dq.front() < i - k  + 1) dq.pop_front();
        
        // 入队一个新元素 在队尾保持队列的单调性
        // 弹出所有比队尾小的元素 更前更小的元素是没有用的
        // 相等的元素也弹出 更新的元素会在窗口中呆的更久
        while(dq.size() && array[dq.back()] <= array[i]) dq.pop_back();
        
        // 将当前元素入队
        dq.push_back(i);
        
        if(i >= k) printf("%d " , array[dq.front()]);
    }   
}
```

### 解法2 

手写双端队列，速度更快。`300ms`

```cpp
#include<iostream>
using namespace std;

const int N = 1e6 + 10;
int array[N] , q[N] , front = 0 , rear = -1;

int main()
{
    int n , k; cin >> n >> k;
    
    for(int i = 1 ; i <= n ; i++)
        scanf("%d" , &array[i]);
    
    for(int i = 1 ; i <= n ; i++)
    {
        if(rear >= front && q[front] < i - k + 1) front++;
        
        while(rear >= front && array[q[rear]] >= array[i]) rear --;
        
        q[++rear] = i;
        
        if(i >= k) printf("%d " , array[q[front]]);
    }
    
    puts("");
    
    front = 0 , rear = -1;
    
    for(int i = 1 ; i <= n ; i++)
    {
        if(rear >= front && q[front] < i - k + 1) front++;
        
        while(rear >= front && array[q[rear]] <= array[i]) rear --;
        
        q[++rear] = i;
        
        if(i >= k) printf("%d " , array[q[front]]);
    }
}
```

## 例题2

> [84.最大矩形纸片](https://leetcode.cn/problems/largest-rectangle-in-histogram/description/)

### 思路

每个矩形可以视作是从某个长方形纸片向外延伸的，我们求出每个长方形纸片可以延展出的矩形的最大面积，即为问题的解。

最大面积的计算方式 = 横向延伸的距离 * 纸片高度。

横向延伸的距离为 向左向右延伸的距离之和。

## 代码

```cpp
// 83% 83%
const int N = 1e5;
int s[N] , top = -1;

class Solution {
public:
    int largestRectangleArea(vector<int>& heights) {
        const int n = heights.size();
        
        int left[n] , right[n];
        
        for(int i = 0 ; i < n; i++)
        {
            // 如果当前柱子小于栈顶 则可以向左延伸
            // 不断弹出栈顶直到不能向左延伸 即找到了向左延伸的最远距离
            // 这时入队当前纸片 刚刚弹出的纸片不会对后续纸片的计算产生影响
            while(top != -1 && heights[s[top]] >= heights[i]) {
                // 对于新的纸片 我们从当前位置向左看递减的纸片 确定其可以向左延伸的距离
	            // 对于弹出的纸片 从弹出位置向右递增看纸片 其向右可以延伸的最远距离距离 为 i
                right[s[top]] = i - 1;
                top --;
            }

            left[i] = top == -1 ? 0 : s[top] + 1;

            s[++top] = i;       
        }
        
        while(top != -1) {
            right[s[top]] = n - 1;
            top --;
        }

        int max_size = 0;
        
        for(int i = 0 ; i < n ; i++)
        {
            max_size = max(max_size , heights[i] * (right[i] - left[i] + 1));
        }

        return max_size;
    }
};
```







