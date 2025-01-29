---
title: String array convertion.
createTime: 2024-12-19
tags:
  - golang
author: ZQ
permalink: /golang/memory/string/convert/array/
---

关于 `golang`中 `string` 和 `array`的转换问题。

<!-- more -->

## 概述

`string`在`golang`中是不可变类型，一般来说讲其转为其他对象会发生拷贝，有什么方法可以不发生拷贝呢。

## 代码实验

```go
package stringtoslice

import (
	"fmt"
	"testing"
	"unsafe"
)

func TestStringToByteArray(t *testing.T) {
	// 创建一个字符串
	s := "hello"

	// 将字符串转换为字节数组
	b := []byte(s)

	// 打印字符串和字节数组的内存地址
	fmt.Println(unsafe.Pointer(&s), unsafe.Pointer(&b))
	// 0xc00002e280 0xc0000100a8 不同地址

	// 拿到 string 的 string header
	// 将 string header 指针强转为一个 [2]int 数组指针 再解引用得到这个数组
	// [5489351 5] 5489351 是底层数组的地址 5 是字符串的长度
	StringHeaderArray := *(*[2]int)(unsafe.Pointer(&s))
	fmt.Println(StringHeaderArray)

	// StringHeaderSlice 是一个 [2]int 数组 字面量 把它强转为一个 []byte 数组指针 再解引用
	// 输出得到这个数组
	b1 := *(*[]byte)(unsafe.Pointer(&StringHeaderArray))
	fmt.Println(b1)

	// 简写为 直接强转为一个 []byte对象的指针
	convertArray := *(*[]byte)(unsafe.Pointer(&s))
	fmt.Println(convertArray)

	fmt.Println((*(*[2]int)(unsafe.Pointer(&s)))[0], (*(*[2]int)(unsafe.Pointer(&s)))[1])
	fmt.Println((*(*[3]int)(unsafe.Pointer(&convertArray)))[0], (*(*[3]int)(unsafe.Pointer(&convertArray)))[1], (*(*[3]int)(unsafe.Pointer(&convertArray)))[2])
	// 5489287 5
	// 5489287 5 0 使用了同一块内存，但是array的容量为0

	// 试图向字节数组追加一个感叹号
	convertArray = append(convertArray, '!')

	fmt.Println(convertArray)
	fmt.Println(s)
	// [104 101 108 108 111 33]
	// hello  hello 没有变化

	fmt.Println((*(*[2]int)(unsafe.Pointer(&s)))[0], (*(*[2]int)(unsafe.Pointer(&s)))[1])
	fmt.Println((*(*[3]int)(unsafe.Pointer(&convertArray)))[0], (*(*[3]int)(unsafe.Pointer(&convertArray)))[1], (*(*[3]int)(unsafe.Pointer(&convertArray)))[2])
	// 5489287 5 字符串的底层数组仍然在原地
	// 824633795440 6 8 // 因为发生扩容， go runtime 将array移动到了别的位置
}
```

## `string` 实现

```go
// +--------------------+       +----------------------------+
// |   StringHeader     |       |   Go String (Immutable)    |
// +--------------------+       +----------------------------+
// | Data (uintptr)     |  ---> |  Data (pointer to bytes)   |
// | Len (int)          |       |  Len (length of string)    |
// +--------------------+       +----------------------------+
//    ^
//    | (points to string's data)
//    v
// +----------------------------+
// |  Byte Array (Underlying Data) |
// +----------------------------+
// |  h  |  e  |  l  |  l  |  o  |
// +----------------------------+
//
```

+ 不可变类型`String`由 `StringHeader` + 底层数组实现。

## `[]byte` 字符切片

```go
// +--------------------+       +----------------------------+
// |     SliceHeader    |       |        Go []byte           |
// +--------------------+       +----------------------------+
// | Data (uintptr)     |  ---> |  Data (pointer to bytes)   |
// | Len (int)          |       |  Len (length of slice)     |
// | Cap (int)          |       |  Cap (capacity of slice)   |
// +--------------------+       +----------------------------+
//	^
//	|  (points to slice's data)
//	v
// +----------------------------+
// |  Byte Array (Underlying Data) |
// +----------------------------+
// |  h  |  e  |  l  |  l  |  o  |
// +----------------------------+
```

## 核心代码解析

+ 将StringHeader 转为 字符切片的指针 `[data][len] -> [data][ptr][0]` 这个过程发生了类型转换，当然也发生了拷贝。由于 `SliceHeader`多一个容量属性，该属性在强转时被自动设为零。

```go
convertArray := *(*[]byte)(unsafe.Pointer(&s)) 
```

+ 类型转化之后，`SliceHeader`和 `StringHeader`有相同的 `data` 和 `len`。所以它们可以使用一样的底层数据。

+ 若要查看 `StringHeader`或者`SliceHeader`中的内容

```go
fmt.Println((*(*[2]int)(unsafe.Pointer(&s)))[0], (*(*[2]int)(unsafe.Pointer(&s)))[1])
```

将他们指向`StringHeader`结构的`Pointer`,类型为 `*StringHeader`, 转换为指向`[2]int`即`[data][len]`数组的指针，指针类型为`*[2]int1`。

## 扩容时拷贝

当对这个“切片”执行 append 时，Go 会发现 “当前容量 = 0，不足以容纳新的元素”，因此必然要**重新分配一块新内存**（扩容）并把老数据拷贝过去


