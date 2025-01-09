---
title: P1 - Two Sum
createTime: 2024-9-3
tags:
  - leetcode
  - hash
  - table
author: ZQ
permalink: /leetcode/hot100/p1/
---

Quick link to leetcode -> [Two Sum](https://leetcode.cn/problems/two-sum/description/)

<!-- more -->

## 1. 两数之和(Easy)

给定一个整数数组 `nums` 和一个整数目标值 `target`，请你在该数组中找出 **和为目标值**`target` 的那 *
*两个** 整数，并返回它们的数组下标。
你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。
你可以按任意顺序返回答案。

## 实现

```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int , int> dict;
        for(int i = 0 ; i < nums.size() ; i++)
        {
            int partner = target - nums[i];
            // 如果有对应的数字 直接返回答案
            if (dict.contains(partner)) return {dict[partner] , i};
            // 否则将这个数字和下标加入哈希表中
            dict[nums[i]] = i;
        }
        return {};
    }
};
```