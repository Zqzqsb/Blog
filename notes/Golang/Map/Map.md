---
title: Map
createTime: 2024-11-6
tags:
  - Golang
description: 笔记记录了Golang中的Map相关。
permalink: /note/golang/map/
---
 笔记记录了Golang中的Map相关。
<!-- more -->

## 概述

`map`，`go`中的哈希表。

`key` 是可哈希的内置对象(`string、int、float`)，或者实现了`hash()`方法的自定义对象。

`value`可以是任意类型。

## 性能

`map` 传递给函数的代价很小：在 32 位机器上占 4 个字节，64 位机器上占 8 个字节，无论实际上存储了多少数据。通过 `key` 在 `map` 中寻找值是很快的，比线性查找快得多，但是仍然比从数组和切片的索引中直接读取要慢 100 倍。

## 创建

map 是 **引用类型** 的： 内存用 make 方法来分配。

map 的初始化：`var map1 = make(map[keytype]valuetype)`。
或者简写为：`map1 := make(map[keytype]valuetype)`。

## 用法示例

```go
package main

import "fmt"

func main() {
	m := make(map[string]int) // create
	m["one"] = 1              // insert
	m["two"] = 2

	fmt.Println(m)                  // formart printer
	fmt.Println(m["one"], m["two"]) // retrieve
	fmt.Println(m["unknown"])       // 0

	r, ok := m["unknown"]
	fmt.Println(r == ok) // false

	delete(m, "one")

	m2 := map[string]int{"one": 1, "two": 2}
	var m3 = map[string]int{"one": 1, "two": 2}
	fmt.Println(m2, m3)

	// traverse
	for item, idx := range m2 {
		fmt.Println(item, idx)
	}
}
```

**输出**

```
map[one:1 two:2]
1 2
0
false
map[one:1 two:2] map[one:1 two:2]
```

## `map` 容量

和数组不同，map 可以根据新增的 `key-value` 对动态的伸缩，因此它不存在固定长度或者最大限制。但是你也可以选择标明 `map` 的初始容量 `capacity`，就像这样：`make(map[keytype]valuetype, cap)`。例如：

```
map2 := make(map[string]float32, 100)
```

当 map 增长到容量上限的时候，如果再增加新的 key-value 对，map 的大小会自动加 1。所以出于性能的考虑，对于大的 map 或者会快速扩张的 map，即使只是大概知道容量，也最好先标明。

## 用切片作为 map 的值

```go
mp1 := make(map[int][]int)
mp2 := make(map[int]*[]int)
```

处理一个健对应多个值的情况。

## 遍历

`map`支持遍历，可以和`for-range`配合使用，遍历的顺序是随机的。

- **遍历桶**：遍历时，Go 首先会遍历 `map` 中的每个桶。遍历的顺序并不是线性的，而是随机的，以避免程序依赖遍历顺序。
- **遍历桶内元素**：在每个桶内，Go 遍历存储的键值对。如果一个桶有溢出桶，则继续遍历溢出桶中的键值对。
- **随机化遍历顺序**：每次遍历时，Go 会使用一个随机的顺序。这是为了避免程序依赖遍历顺序，确保遍历顺序不会随着键的插入顺序改变而固定。

## `map`的切片

假设我们想获取一个 `map` 类型的切片，我们必须使用两次 `make()` 函数，第一次分配切片，第二次分配 切片中每个 `map` 元素。

这样理解这件事情，比如需要在`C++`中分配一个`vector<int>`数组。写法为

```cpp
vector<int> va[10];
```
### 数组部分的内存

`std::vector<int> va[10];`

这段代码创建了一个长度为 10 的数组 `va`，其中每个元素是一个 `std::vector<int>` 类型的对象。这个数组本身是在栈上分配的，因此，**`va` 数组的内存是固定且静态的**，大小是 10。

- `va` 数组中每个元素（即 `std::vector<int>`）是一个对象，它的内存会在栈上分配，类似于普通的对象，但它是一个 **包含指向动态内存的指针的类**。

### `vector<int>` 内部的内存管理

`std::vector<int>` 是一个动态数组，它的内部机制是动态分配内存来存储元素。具体来说，`std::vector<int>` 存储的数据是通过 **堆** 动态分配的，而不是直接存储在栈上。因此，虽然 `va` 数组本身在栈上分配内存，但是每个 `std::vector<int>` 内部的数据是动态分配的。

再回头看`map`的切片,也是两次构造的过程。首先需要为切片的底层数组分配内存并且创建切片，再为切片中的每个`map`分配内存。这里`map`是个引用类型，这种方式的内存分配方式和`vector<int>是一致的。

```go
package main
import "fmt"

func main() {
	// Version A:
	items := make([]map[int]int, 5)
	for i:= range items {
		items[i] = make(map[int]int, 1)
		items[i][1] = 2
	}
	fmt.Printf("Version A: Value of items: %v
", items)

	// Version B: NOT GOOD!
	items2 := make([]map[int]int, 5)
	for _, item := range items2 {
		item = make(map[int]int, 1) // item is only a copy of the slice element.
		item[1] = 2 // This 'item' will be lost on the next iteration.
	}
	fmt.Printf("Version B: Value of items: %v
", items2)
```

**输出**

```
Version A: Value of items: [map[1:2] map[1:2] map[1:2] map[1:2] map[1:2]]
Version B: Value of items: [map[] map[] map[] map[] map[]]
```

这里`range` 函数的特性是返回元素的拷贝，所以是创建行为`B`是不成功的。

## `map`的排序

`map` 默认是无序的，不管是按照 `key` 还是按照 `value` 默认都不排序。

如果想为 `map` 排序，需要将 `key` 拷贝到一个切片，再对切片排序。
