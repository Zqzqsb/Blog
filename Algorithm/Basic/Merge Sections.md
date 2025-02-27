---
title: Merge Sections
createTime: 2023-8-3
author: ZQ
permalink: /algorithm/basic/merge_sections/
---

![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E7%AE%97%E6%B3%95_%E5%8C%BA%E9%97%B4%E5%90%88%E5%B9%B6/%E5%B0%81%E9%9D%A2.png)
 本文讲述了基础算法中区间合并的相关内容。
 
<!-- more -->

##  区间合并

区间合并将一系列分散合并为一个或多个区间，其核心步骤根据区间的左端点进行排序。

下图很好地展示了这一过程。

![区间合并](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/%E7%AE%97%E6%B3%95_%E5%8C%BA%E9%97%B4%E5%90%88%E5%B9%B6/%E5%8C%BA%E9%97%B4%E5%90%88%E5%B9%B6.png)

```c++
#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;
// 存储区间的左右端点

// pair 可以将两个数据封装在一个结构体内
typedef pair<int , int> PII;

const int N = 100010;

int n;
vector<PII> segs;

void merge(vector<PII>& segs)
{
    vector<PII> res;
    // 按照区间的左端点排序
    sort(segs.begin(), segs.end());

    // 初始化维护区间
    int st = -2e9 , ed = -2e9;

    // 遍历所有的区间
    for(auto seg : segs)
    {
        // 如果新区间 在当前维护区间的右边 将当前维护的区间加入结果 并且构造新的维护区间
        if(ed < seg.first)
        {
            if(st != -2e9) res.push_back({st , ed});
            st = seg.first , ed = seg.second;
        }
        else // 否则重置维护区间的末端点 为当前维护区间和新区间较大的那个
            ed = max(ed , seg.second);
    }

    // 如果区间不为初始值 那么将一个维护区间加入结果
    if(st != -2e9) res.push_back({st , ed});

    // 将结果写回
    segs = res;
}

int main()
{
    // 按所有的左端点从小到大排序
    cin >> n; // 读入n个端点
    for(int i = 0 ; i < n ; i++)
    {
        int l , r;
        cin >> l >> r; // 读入区间
        segs.push_back({l , r}); // 将区间读入到segs
    }

    merge(segs); // 合并

    cout << segs.size() << endl;
}
```
