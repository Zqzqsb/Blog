---
title: Variant of Bag Problems
tags:
  - 背包问题
  - 动态规划
createTime: 2024-2-17
author: ZQ
permalink: /algorithm/dp/bag_variant/
---

![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/variants_of_bag_problem/cover.png)
 这篇文章详细分析背包问题的变形问题。
 
<!-- more -->

## 前言

在阅读篇文章之前你可能需要首先阅读[01 背包问题](https://blog.zqzqsb.cn/2024/02/16/01%E8%83%8C%E5%8C%85%E9%97%AE%E9%A2%98/),以对背包问题有一个基本的了解。

## 完全背包问题

### 前提

完全背包解除了物品数量的限制，使得所有的所有的物品都可以无限量供应。

**试一试**

- [完全背包](https://www.acwing.com/problem/content/3/)

### 递推

我们仍考虑是否要将第 i 个物品装入背包。默认仍不装入这个物品。

```c++
f[i][j] = f[i-1][j];
```

接下来相比于 01 背包的改变是，当我们有机会装入第 i 个物品时，我们仍可以**继续考虑装入第 i 个物品**。

```c++
if(j >= weights[i]) f[i][j] = max(f[i][j] , f[i][j-weights[i]] + values[i]);
```

所以在 `f[i][j-weights[i]] + values[i]` 中, i 并不需要减少。另外可以想见，在递推中所需求的位置是有解的。
![安全背包递推](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/variants_of_bag_problem/complete_bag_1.png)

### 优化

根据先前的优化思路，我们仍可以将这个过程中的空间优化至一维。在 01 背包中，递推时需要的是对于 **前 i -1 物品所构成的装填方案** 的所有正确的解，所以我们要保留先前的解，这才从行的末尾向前递推。

而在完全背包中，递推一个新的位置需求的是 对于 **前 i 物品所构成的装填方案** 而将新旧行交替时，必须从左往右递推，逐步替代掉上一行的旧解。0 - weights\[i] 这些位置不能装载第 i 个物品，所以直接保留上一行的解，从 weights\[i]开始递推至行末尾即可。
![完全背包行交替](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/variants_of_bag_problem/complete_bag_2.png)

### 优化代码

```c++
#include<iostream>
using namespace std;
const int N = 1e3 + 10;
int weights[N] , values[N];
int f[N];

int main()
{
    int N , V; cin >> N >> V;
    for(int i = 1 ; i <= N ; i++)
        cin >> weights[i] >> values[i];

    for(int i = 1 ; i <= N ; i++)
    {
        for(int j = weights[i] ; j <= V ; j++)
        {
            f[j] = max(f[j] , f[j-weights[i]] + values[i]);
        }
    }
    cout << f[V];
}
```

## 多重背包问题

### 前提

多重背包的限制条件介于 01 背包和完全背包之间，为每种物品增加数量上限。

**试一试**

- [多重背包 1](https://www.acwing.com/problem/content/4/)
- [多重背包 2](https://www.acwing.com/problem/content/5/)

### 读入

多添加一个 nums 数组以存储数量信息。

```c++
int weights[N] , values[N] , nums[N];
```

### 递推

相信已经轻车熟路，仍从不装入第 i 个物品开始考虑。

```c++
f[i][j] = f[i-1][j];
```

接着我们考虑装入装入第 i 个物品的数量，通过枚举实现。这里有两个限制

- 数量不能超过给定的上限
- 总体积不能超过背包在**当前子问题中的容量**

```c++
for(int k = 1 ; k <= nums[i] && k * weights[i] <= j; k++)
{
	f[i][j] = max(f[i][j] , f[i-1][j-k*weights[i]] + k * values[i]);
}
```

**说明**

- 这里当第 i 物品的数量确定，就不能再选择，所以` f[i-1][j-k*weights[i]]`此处 i 减了一。
- 装入第 k 个 i 号物品，要减去 k 份体积，加上 k 个价值。

从 k = 0 开始枚举时，这两种情况可以合并，写作

```c++
for(int k = 0 ; k <= nums[i] && k * weights[i] <= j; k++)
{
	f[i][j] = max(f[i][j] , f[i-1][j-k*weights[i]] + k * values[i]);
}
```

### 空间优化

这里递推时利用的上一行的信息，所以在使用滚动数组时，仍是从尾部向前计算新行。原理和之前类似，这里不再给出图解。

```c++
#include<iostream>
using namespace std;

const int N = 110;
int weights[N] , values[N] , nums[N];
int f[N];

int main()
{
    int N , V; cin >> N >> V;

    for(int i = 1 ; i <= N ; i++)
        cin >> weights[i] >> values[i] >> nums[i];


    for(int i = 1 ; i <= N ; i++)
    {
        for(int j = V ; j >= weights[i] ; j--)
        {
            for(int k = 0 ; k <= nums[i] && k * weights[i] <= j; k++)
            {
                f[j] = max(f[j] , f[j-k*weights[i]] + k * values[i]);
            }
        }
    }
    cout << f[V];
}
```

### 时间优化

#### 二进优化原理

对于这个问题，其计算复杂度为 `O(N * V * K)`。我们可以考虑在枚举 K 时实施二进制优化。枚举 K 的目的是一个怎样的过程？我们为了确定在当前的背包容量下的最佳装填方案是什么。而这个最佳装填方案对应了一个确定的 K 值，所以枚举所有可能的 K。

![枚举K](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/variants_of_bag_problem/complete_bag_3.png)

我们可以这样构造它的一个等价问题。假设我们所有第 i 个物品分为 1 , 2 , 4 , 8 ...... 这样的组。满足最后一个非 2 进制数组大于前一个组。
![分组](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/variants_of_bag_problem/complete_bag_4.png)
现在思考这也一个问题，我们在考虑第 i 个物品时，必须考虑装入一个整个组，以此来求解`f[i][j]`的最大值。这是否和之前是一样的问题?

**证明**
它们是一样的问题。因为`1 - nums[i]`中的任何一个 K，都可以找到一种对应分组选择方案。可以递推这证明这一点。

- 1 , 2 可以表示出 `[1 , 3]`中任何一个数
- `[1 , 3]` 和 4 可以表示 `[1 , 7]`中的任何一个数。
- `[1 , 7]` 和 8 可以表示 `[1 , 15]`中的任何一个数。
- `[1 , 15]` 和 `nums[i] - 8` 可以表示出`[1 , nums[i]]`中的任何一个数。

现在构造并且求解这样的等价问题。

### 代码

```c++
#include<iostream>
#include<cmath>
using namespace std;

const int N = 2010 * 12;
int values[N] , weights[N] , group = 0;
int f[2010];

int main()
{
    int N , V; cin >> N >> V;

    for(int i = 1 ; i <= N ; i++)
    {
        int w , v , s;
        cin >> w >> v >> s;

        int k = 1;
        while(s > k)
        {
            group++;
            weights[group] = k * w;
            values[group] = k * v;

            s -= k;
            k *= 2;
        }

        if(s)
        {
            group++;
            weights[group] = s * w;
            values[group] = s * v;
        }
    }

    for(int i = 1 ; i <= group ; i++)
    {
        for(int j = V ; j >= weights[i] ; j--)
        {
            f[j] = max(f[j] , f[j-weights[i]] + values[i]);
        }
    }

    cout << f[V];
}
```

**说明**

1. 分组会导致物品数量数量变多，在存储需要开辟额外的空间。
2. 分完组之后，根据先前的推导，这个问题变成了一个 01 背包问题。

## 分组背包

### 前提

**限制**
为所有物品分组，限定只能从每组中拿出一个物品。

**试一试**

- [分组背包](https://www.acwing.com/problem/content/9/)

### 读入

使用额外的空间来记录每组内物品数量，将每组物品存入二维数组的行中。

```c++
const int N = 110;
int numInGroups[N]; // 保存每组有多少物品
int weights[N][N] , values[N][N]; // 每组物品的体积和价值
int f[N][N]; // dp表
```

### 递推

考虑是否装入第`i`组的物品，如果装入，那么枚举得到子问题的最佳解。

```c++
f[i][j] = f[i-1][j]; // 不装入第i组的物品
// 枚举
for(int k = 1 ; k <= numInGroups[i] ; k++)
{
	if(weights[i][k] <= j)
		f[i][j] = max(f[i][j] , f[i-1][j-weights[i][k]] + values[i][k]);
}
```

### 完整代码

```c++
#include<iostream>
using namespace std;

const int N = 110;
int numInGroups[N]; // 保存每组有多少物品
int weights[N][N] , values[N][N]; // 每组物品的体积和价值
int f[N][N]; // dp表

int main()
{
    int N , V; cin >> N >> V;

    for(int i = 1 ; i <= N ; i++)
    {
        cin >> numInGroups[i];
        for(int j = 1 ; j <= numInGroups[i] ; j++)
        {
            cin >> weights[i][j] >> values[i][j];
        }
    }

    for(int i = 1 ; i <= N ; i++)
    {
        for(int j = 1 ; j <= V ; j++)
        {
            f[i][j] = f[i-1][j];
            for(int k = 1 ; k <= numInGroups[i] ; k++)
            {
                if(weights[i][k] <= j)
                    f[i][j] = max(f[i][j] , f[i-1][j-weights[i][k]] + values[i][k]);
            }
        }
    }

    cout << f[N][V];
}
```
