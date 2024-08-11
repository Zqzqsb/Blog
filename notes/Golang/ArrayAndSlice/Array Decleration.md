---
title: Arrays and Slice in Golang.
createTime: 2024-8-7
tags:
  - Golang
description: 笔记记录了Golang中的数组和切片。
---
<br> 笔记记录了Golang中的数组和切片。
<!-- more -->

## 概述

`go`在数组和切片的设计上明显收到`python`的影响。

以  `[]`  符号标识的数组类型几乎在所有的编程语言中都是一个基本主力。Go 语言中的数组也是类似的，只是有一些特点。Go 没有 C 那么灵活，但是拥有切片（slice）类型。这是一种建立在 Go 语言数组类型之上的抽象，要想理解切片我们必须先理解数组。数组有特定的用处，但是却有一些呆板，所以在 Go 语言的代码里并不是特别常见。相对的，切片确实随处可见的。它们构建在数组之上并且提供更强大的能力和便捷

## 声明和初始化

### 概述

数组是具有相同  **唯一类型**  的一组已编号且长度固定的数据项序列（这是一种同构的数据结构）；这种类型可以是任意的原始类型例如整型、字符串或者自定义类型。数组长度必须是一个常量表达式，并且必须是一个非负整数。数组长度也是数组类型的一部分，所以`[5]int` `[10]int`是属于不同类型的。数组的编译时值初始化是按照数组顺序完成的。

数组元素可以通过  **索引**（位置）来读取（或者修改），索引从 0 开始，第一个元素索引为 0，第二个索引为 1，以此类推。（数组以 0 开始在所有类 C 语言中是相似的）。元素的数目，也称为长度或者数组大小必须是固定的并且在声明该数组时就给出（编译时需要知道数组长度以便分配内存）；数组长度最大内存用量 `2Gb` (`256MB` , 大约`2^28`个`int32`)

数组声明的格式

```go
var identifier [len]type
```

例如

```go
var arr1 [5]int
```

## 遍历
### 遍历数组

**写法一**

```go
package main
import "fmt"

func main() {
	var arr1 [5]int

	for i:=0; i < len(arr1); i++ {
		arr1[i] = i * 2
	}

	for i:=0; i < len(arr1); i++ {
		fmt.Printf("Array at index %d is %d
", i, arr1[i])
	}
}
```

输出

```
Array at index 0 is 0
Array at index 1 is 2
Array at index 2 is 4
Array at index 3 is 6
Array at index 4 is 8
```

**写法二**

```go
package main
import "fmt"

func main() {
	var arr1 [5]int

	for i , _ := range arr1 {
		fmt.Printf("index: %d , value: %d
" , i , arr1[i]);
	}

}
```

输出

```shell
index: 0 , value: 0
index: 1 , value: 0
index: 2 , value: 0
index: 3 , value: 0
index: 4 , value: 0
```

### 遍历串

```go
a := [...]string {"a", "b", "c", "d"}
for i := range a {
	fmt.Println("Array item", i, "is", a[i])
}
```


## 数组元素的类型

```go
var arr1 = new([5]int)
```

`arr1`的类型是 `*[5]int` , 以`c++`的方式理解，是个指针(引用)类型。

```go
var arr2 [5]int
```

`arr2`的类型是 `[5]int` , 是一种值类型。

### 深浅拷贝

#### 浅拷贝例子

```go
var arr1 = new([5]int)
arr1[3] = 100
var arr2 = arr1 // shallow copy
arr2[3] = 99
fmt.Println("%d %d", arr1[3], arr2[3])
```

```shell
99 99
```

#### 深拷贝的例子

```go
var arr3 [5]int = [...]int{1, 2, 3, 4, 5}
arr3[3] = 100
var arr4 = arr3 // deep copy
arr4[3] = 99
fmt.Println("%d %d", arr3[3], arr4[3])
```

```shell
100 99
```

### 参数传递

```go
package main
import "fmt"
func f(a [3]int) { fmt.Println(a) }
func fp(a *[3]int) { fmt.Println(a) }

func main() {
	var ar [3]int
	f(ar) 	// passes a copy of ar
	fp(&ar) // passes a pointer to ar
}
```

\
## 数组常量

如果数组值已经提前知道了，那么可以通过 **数组常量** 的方法来初始化数组。

### 写法一 

```go
var arrAge = [5]int{18, 20, 15, 22, 16}
```

支持部分初始化，类似`[10]int {1 , 2 , 3}` 未初始化的位置都为零。

### 写法二

```go
var arrLazy = [...]int{5, 6, 7, 8, 22}
```

类似于一种解包操作。

### 写法三

```go
var arrKeyValue = [5]string{3: "Chris", 4: "Ron"}
```

`key-value`语法，赋值特定的位置。


## 多维数组

```go
package main
const (
	WIDTH  = 1920
	HEIGHT = 1080
)

type pixel int
var screen [WIDTH][HEIGHT]pixel

func main() {
	for y := 0; y < HEIGHT; y++ {
		for x := 0; x < WIDTH; x++ {
			screen[x][y] = 0
		}
	}
}
```
