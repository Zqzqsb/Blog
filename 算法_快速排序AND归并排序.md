---
title: 快速排序AND归并排序
categories: 算法
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/%E7%AE%97%E6%B3%95/%E7%AE%97%E6%B3%95_%E5%BF%AB%E9%80%9F%E6%8E%92%E5%BA%8FAND%E5%BD%92%E5%B9%B6%E6%8E%92%E5%BA%8F/%E5%B0%81%E9%9D%A2.gif
date: 2022-1-10
description: 本文讲解了快速排序和归并排序的实现方法。
---

# 快速排序 

快速排序基于分治思想 可以分为三个步骤

+ 选定分界点 可以取两端点 中点或随机点
+ 使用快慢指针 进行数组分割
+ 对子数组递归的使用快排

快排可以是稳定的 取决于具体的做法

完整代码

```C++
void QuickSort(int a[] , int start , int end)
{
    if(start >= end) //终止条件
        return;
    int p = a[end]; // 分割点
    int i = start , j = start; // 快慢指针
    for( ; j < end ; j++) // 快指针前进搜索 start ~ end-1
    {
        if(a[j] <= p)
        {
            swap(a[i++] , a[j]); // 将小元素交换给慢指针
        }
    }
    swap(a[i] , a[end]); // 交换慢指针所在位置和分割点
    QuickSort(a , start , i-1); // 对两端区间分别做快排
    QuickSort(a , i+1 , end);
}
```

# 归并排序

归并排序同样基于分治思想

+ 分割序列 直到每个序列长度为1 此时每个子序列是有序的
  + 先分割意味着递归在代码的前部
+ 接着不断合并有序数组 直到整个数组都有序

```c++
void MergeSort(int a[] , int start , int end)
{
    if(start >= end) // 终止条件
        return;

    // 分割区间
    int mid = (start + end) / 2; 
    MergeSort(a , start , mid);
    MergeSort(a , mid+1 , end);

    // 在运行到这一步时 start-mid , mid+1 - end 分别为两段有序序列
    int t[end - start+1] , i = 0; // 临时数组和插入位置指针
    int l = start , r = mid+1; // 左右子数组中的指针

    // 合并
    while(l <= mid && r <= end) 
        t[i++] = a[l] < a[r] ? a[l++] : a[r++];
    while(l <= mid)
        t[i++] = a[l++];
    while(r <= end)
        t[i++] = a[r++];

    // 将临时数组的内容写回原数组
    for(i = 0 ; i < end-start+1 ; i++) 
    {
        a[start + i] =  t[i];
    }
}
```



