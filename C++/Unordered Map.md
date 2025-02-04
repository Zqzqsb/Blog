---
title: Concept of Hashing
categories:
  - 算法
tags:
  - 哈希
  - stl
createTime: 2024-10-10
permalink: /algorithm/hash/unordered_map/
---

本文部分解读了 `C++ STL` 的`unordered_map`实现。

<!-- more -->

## 头文件解读

###  模板类

`unordered_map` 是模板类，可以接受五个模板参数：键类型、值类型、哈希函数、相等性比较器和分配器。

```cpp
template<typename _Key, typename _Tp, typename _Hash = hash<_Key>,
         typename _Pred = equal_to<_Key>, typename _Alloc = allocator<pair<const _Key, _Tp>>>
```

> 其中`_Hash` 默认使用 `std::hash<_Key>`， 用于哈希计算; `_Pred` 默认为 `std::equal_to<_Key>`，用于比较键是否相等；`_Alloc` 默认使用 `std::allocator`，管理内存分配。

### 类定义

```cpp
  typedef __umap_hashtable<_Key, _Tp, _Hash, _Pred, _Alloc> _Hashtable;
  _Hashtable _M_h;
```

这定义了 `unordered_map` 的基本结构。它将 `_Hashtable` 定义为 `unordered_map` 的内部存储类型，并实例化了一个 `_M_h` 成员变量，这是底层的哈希表。

类中还包含了一些类型别名，例如 `key_type`、`value_type` 和 `allocator_type`，方便用户在使用时引用类型。

### 构造函数

```cpp
unordered_map();
explicit unordered_map(size_type __n, const hasher& __hf = hasher(),
                       const key_equal& __eql = key_equal(),
                       const allocator_type& __a = allocator_type());
```

这些构造函数提供了创建 `unordered_map` 对象的多种方式，包括默认构造函数、指定哈希函数和相等性比较器的构造函数、以及从范围或初始化列表创建对象的构造函数。

### 迭代器

```cpp
iterator begin() noexcept;
const_iterator begin() const noexcept;
iterator end() noexcept;
const_iterator end() const noexcept;
```

这些迭代器接口允许用户访问 unordered_map 中的元素。`begin()` 和 `end()` 分别返回起始和结束位置的迭代器，`cbegin()` 和 `cend()` 提供了常量版本。

### 修改操作

+ 插入和删除：包括 `insert()`,`erase()`,`clear()` 等操作，用于管理元素的添加、删除和清空

```cpp
pair<iterator, bool> insert(const value_type& __x);
iterator erase(const_iterator __position);
void clear() noexcept;
```

 + 特殊插入方法：如 `emplace()` 和 `try_emplace()`，允许原位构造元素，以提高效率。

### 哈希和比较函数

hash_function() 和 key_eq() 返回哈希函数对象和键比较函数对象：

```cpp
hasher hash_function() const;
key_equal key_eq() const;
```

### 负载因子和哈希策略

`load_factor()` 和 `max_load_factor()` 控制和查询哈希表的负载因子，`rehash()` 和 `reserve()` 用于调整哈希表的大小。

```cpp
float load_factor() const noexcept;
float max_load_factor() const noexcept;
void rehash(size_type __n);
void reserve(size_type __n);
```


## 代码示例

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    // 创建一个unordered_map，键为string，值为int
    std::unordered_map<std::string, int> myMap;

    // 插入键值对
    myMap["apple"] = 3;
    myMap["banana"] = 5;
    myMap["orange"] = 2;

    // 使用insert方法插入键值对
    myMap.insert({"grape", 4});

    // 访问元素（使用operator[]）
    std::cout << "apple: " << myMap["apple"] << std::endl;

    // 访问元素（使用at()，可检查键是否存在）
    try {
        std::cout << "banana: " << myMap.at("banana") << std::endl;
    } catch (const std::out_of_range& e) {
        std::cout << "Key not found: " << e.what() << std::endl;
    }

    // 检查是否包含某个键（使用count()）
    if (myMap.count("orange") > 0) {
        std::cout << "orange is in the map." << std::endl;
    } else {
        std::cout << "orange is not in the map." << std::endl;
    }

    // 删除元素
    myMap.erase("grape");

    // 遍历unordered_map
    std::cout << "Contents of the map:" << std::endl;
    for (const auto& pair : myMap) {
        std::cout << pair.first << ": " << pair.second << std::endl;
    }

    // 清空unordered_map
    myMap.clear();
    std::cout << "Map size after clear: " << myMap.size() << std::endl;

    return 0;
}
```