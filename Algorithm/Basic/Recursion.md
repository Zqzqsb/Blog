---
title: 递归和递推
tags: 
  - 递归
createTime: 2024-1-10
author: ZQ
permalink: /algorithm/basic/recurrence/
---

![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E9%80%92%E5%BD%92%E5%92%8C%E9%80%92%E6%8E%A8/%E4%BF%84%E7%BD%97%E6%96%AF%E5%A5%97%E5%A8%83.png)
 本文介绍了递归和递推的基本思想和典型问题。
 
<!-- more -->

## 前言

递归的求解过程有点像解俄罗斯套娃的过程。
![套娃](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E9%80%92%E5%BD%92%E5%92%8C%E9%80%92%E6%8E%A8/%E4%BF%84%E7%BD%97%E6%96%AF%E5%A5%97%E5%A8%83.png)
必须不断拿掉最顶部的娃，才能得到这个娃的内部。例如要求一组套娃一共有几个，那么便不断拿掉最顶上的娃，每拿掉一个就可以将数量记录加 1。如果用程序表达这一递归式子，便是。

```c++
taowa(n) = taowa(n-1) + 1;
```

而这个过程什么时候终止呢，那便是拿到了最后一个娃。所以也可以写出

```c++
if(n == 1) return;
```

任何一个朴素的递归都考虑这两个点，即**递归式子**和**终止条件**。可以将这一过程完成的写出来。

```c++
#include<iostream>
using namespace std;

int taowa(int n)
{
	// 先写终止条件
	if(n == 1) return 1;
	return taowa(n-1) + 1; // 在解套的过中得到一个新的娃
}
int main()
{
	cout << taowa(6);
}
```

## 从斐波那契数列问题看递归和递推

### 问题

斐波那契是一个经典的问题.
**斐波那契数列：0，1，1，2，3，5，8，……从第三项起，每一项都是紧挨着的前两项的和。写出计算斐波那契数列任意一个数据项的递归程序。**
可以很容易的通过前言的两个原则写出这个程序。

```c++
#include <iostream>
using namespace std;

int fb(int n)
{
	// 因为递归式要利用前两项 所以初始化需要初始化两项
	if(n == 1) return 0;
	if(n == 2) return 1;
	return fb(n-1) + fb(n-2);
}
int main()
{
	int n; cin >> n;
	cout << fb(n);
}
```

### 递归栈

"递归栈" 指的是在递归算法中使用的调用栈（Call Stack）。当一个函数调用另一个函数时，当前函数的状态（局部变量、返回地址等）被保存在调用栈上，新的函数被推入栈顶。当被调用的函数执行完成后，它的状态从栈上弹出，控制权返回给调用它的函数。
递归栈是一块具体的地方，其大小取决于很多因素，如编程语言，编译器和操作系统。而递归栈的大小决定了可以入栈的函数数量。

### 递归中的重复计算

考虑这样的递归链条

```c++
fb(5) = fb(4) + fb(3);
fb(4) = fb(3) + fb(2);
```

可以看到 fb(5) 需求两项，fb(4) 和 fb(3)的解。 而 fb(4)的求解过程也需要 fb(3)的解。可以看出，在这一过程中大量的重复调用。

![重复计算](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E9%80%92%E5%BD%92%E5%92%8C%E9%80%92%E6%8E%A8/duplicate_calculate.png)

### 改善

为了解决上述的两个问题，可以分别引入**动态规划**和**记忆化搜索**两种思想。

- **动态规划** 改变问题的求解的路径，从小的问题开始求解大的问题，使得求解规模不再受制于递归栈的大小限制。
- **记忆化搜索** 在递归过程记录已经求解的值，避免重复的计算。一般用于优化无法转化为正向求解的递归问题。

### 斐波那契的递推的解法

```c++
#include<iostream>
using namespace std;
const int N = 1e5;
int f[N];
int main()
{
	f[1] = 0 , f[2] = 1;
	int n; cin >> n;
	for(int i = 3 ; i <= n ; i++) f[i] = f[i-1] + f[i-2];
	cout << f[n];
}
```

可以将这一过程理解为填满一张 **子问题解答的表格** 并且推导到最终的问题。
