---
title: 最长非重子序列
createTime: 2023-8-3
tags:
  - 滑动窗口
author: ZQ
permalink: /algorithm/basic/LNS/
---

![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E7%AE%97%E6%B3%95_%E6%9C%80%E9%95%BF%E9%9D%9E%E9%87%8D%E5%AD%90%E5%BA%8F%E5%88%97/%E5%B0%81%E9%9D%A2.png)

## 最长非重复子序列

使用双指针算法解决这个问题。 这其中的核心问题是如何记录已经访问的元素和失配(miss match)后的的算法行为。

![示意](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E7%AE%97%E6%B3%95_%E6%9C%80%E9%95%BF%E9%9D%9E%E9%87%8D%E5%AD%90%E5%BA%8F%E5%88%97/%E7%A4%BA%E6%84%8F.png)

```c++
#include <iostream>
using namespace std;

const int N = 100010;
int a[N] , s[200];

// 用s数组纪录元素出现的个数 s的长度只需覆盖ascii码的范围即可
// 每当i前进 就会多记录一个元素 那么和可能重复的元素就是a[i]
// 当重复发生时 (s[a[j]] > 1) 为了消除这种重复 要向前移动j 直到a[i]重新为1
// 每当i增加 记录当前的最大长度

void Longest_NonRepeating_Subsequence()
{
    int n , maxL = 0;
    cin >> n;
    // 将字符串读入数组
    for(int i = 0 ; i < n ; i++) cin >> a[i];

    // 遍历这个串
    for(int i = 0 , j = 0; i < n ; i++)
    {
        s[a[i]]++; // 将这个遇到的元素 计数加一
        while(s[a[i]] > 1) // 如果当前元素的计数大于一 那么不断减少区间的左部分
        {
            s[a[j]]--;
            j++;
        }
        maxL = max(maxL , i - j + 1); // 记录当前区间的长度
    }
    cout << maxL << endl;

}
```
