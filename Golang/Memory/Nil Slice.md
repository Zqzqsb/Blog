---
title: Memory about nil slice and empty slice.
createTime: 2024-12-19
tags:
  - golang
  - memory
author: ZQ
permalink: /golang/memory/nilslice/
---

关于 `golang`中 空切片和 `nil` 切片的内存分配问题。

<!-- more -->

## 概述

`golang`中的空切片和仅申明的`nil`切边有什么不同吗。

## 代码实验

```go
package emptyslice

import (
	"fmt"
	"testing"
	"unsafe"
)

func TestNilSlice(t *testing.T) {

	var s1 []int
	s2 := make([]int, 0)
	s4 := make([]int, 0)

	// +--------------------------+
	// |       Go Slice           |
	// +--------------------------+
	// |   Data (uintptr)         |  ----> (底层数组的指针)
	// +--------------------------+
	// |   Len (int)              |  ----> (切片的长度)
	// +--------------------------+
	// |   Cap (int)              |  ----> (切片的容量)
	// +--------------------------+
	fmt.Printf("s1 pointer:%+v, s2 pointer:%+v, s4 pointer:%+v, \n", *(*[3]uintptr)(unsafe.Pointer(&s1)), *(*[3]uintptr)(unsafe.Pointer(&s2)), *(*[3]uintptr)(unsafe.Pointer(&s4)))
	// s1 pointer:[0 0 0], s2 pointer:[824634189488 0 0], s4 pointer:[824634189488 0 0],
	// nil 切片没有分配底层数组指向的地址是0 s2 , s4 虽然分配了底层数组 但是指向同一个地址

	s1 = append(s1, 1) // 发生了make 分配了底层数组 并且扩容
	s2 = append(s2, 1) // 发生了底层数组的扩容
	fmt.Printf("s1 pointer:%+v, s2 pointer:%+v, s4 pointer:%+v, \n", *(*[3]uintptr)(unsafe.Pointer(&s1)), *(*[3]uintptr)(unsafe.Pointer(&s2)), *(*[3]uintptr)(unsafe.Pointer(&s4)))

	// s1 pointer:[824634909032 1 1], s2 pointer:[824634909040 1 1], s4 pointer:[824634437296 0 0],
	// s4的地址也发生了变化 s2 的扩容影响了 s4 的底层数组分配
}
```
