---
title: Functions in Golang Chapter2.
createTime: 2024-7-17
tags:
  - Golang
description: 笔记记录了Golang中的函数。
permalink: /note/golang/function/2/
---
 笔记记录了Golang中的函数。
<!-- more -->

## defer 和 追踪

### defer 概述

关键字 defer 允许我们推迟到函数返回之前（或任意位置执行 `return` 语句之后）一刻才执行某个语句或函数（为什么要在返回之后才执行这些语句？因为 `return` 语句同样可以包含一些操作，而不是单纯地返回某个值）。

关键字 defer 的用法类似于面向对象编程语言 Java 和 C# 的 `finally` 语句块，它一般用于释放某些已分配的资源。

```go
package main
import "fmt"

func main() {
	function1()
}

func function1() {
	fmt.Printf("In function1 at the top
")
	defer function2()
	fmt.Printf("In function1 at the bottom!
")
}

func function2() {
	fmt.Printf("Function2: Deferred until the end of the calling function!")
}
```

输出：

```
In Function1 at the top
In Function1 at the bottom!
Function2: Deferred until the end of the calling function!
```

请将 defer 关键字去掉并对比输出结果。

使用 defer 的语句同样可以接受参数，下面这个例子就会在执行 defer 语句时打印 `0`：

```go
func a() {
	i := 0
	defer fmt.Println(i)
	i++
	return
}
```

当有多个 defer 行为被注册时，它们会以逆序执行（类似栈，即后进先出）：

```go
func f() {
	for i := 0; i < 5; i++ {
		defer fmt.Printf("%d ", i)
	}
}
```

上面的代码将会输出：`4 3 2 1 0`。

### 使用场景

关键字 defer 允许我们进行一些函数执行完成后的收尾工作，例如：

+ 关闭文件流

```go
defer file.Close()
```

+ 解锁一个加锁的资源

```go
mu.Lock()  
defer mu.Unlock() 
```

+ 打印最终报告

```go
printHeader()  
defer printFooter()
```

+ 关闭数据库链接

```go
defer disconnectFromDB()
```

合理使用 defer 语句能够使得代码更加简洁。

以下代码模拟了上面描述的第 4 种情况：

```go
package main

import "fmt"

func main() {
	doDBOperations()
}

func connectToDB() {
	fmt.Println("ok, connected to db")
}

func disconnectFromDB() {
	fmt.Println("ok, disconnected from db")
}

func doDBOperations() {
	connectToDB()
	fmt.Println("Defering the database disconnect.")
	defer disconnectFromDB() //function called here with defer
	fmt.Println("Doing some DB operations ...")
	fmt.Println("Oops! some crash or network error ...")
	fmt.Println("Returning from function here!")
	return //terminate the program
	// deferred function executed here just before actually returning, even if
	// there is a return or abnormal termination before
}
```

### 代码追踪

一个基础但十分实用的实现代码执行追踪的方案就是在进入和离开某个函数打印相关的消息，即可以提炼为下面两个函数

```go
package main

import "fmt"

func trace(s string)   { fmt.Println("entering:", s) }
func untrace(s string) { fmt.Println("leaving:", s) }

func a() {
	trace("a")
	defer untrace("a")
	fmt.Println("in a")
}

func b() {
	trace("b")
	defer untrace("b")
	fmt.Println("in b")
	a()
}

func main() {
	b()
}
```

输出:

```
entering: b
in b
entering: a
in a
leaving: a
leaving: b
```

上面的代码还可以修改为更加简便的版本

```go
package main

import "fmt"

func trace(s string) string {
	fmt.Println("entering:", s)
	return s
}

func un(s string) {
	fmt.Println("leaving:", s)
}

func a() {
	defer un(trace("a"))
	fmt.Println("in a")
}

func b() {
	defer un(trace("b"))
	fmt.Println("in b")
	a()
}

func main() {
	b()
}
```

**使用 defer 语句来记录函数的参数与返回值**

下面的代码展示了另一种在调试时使用 defer 语句的手法

```go
package main

import (
	"io"
	"log"
)

func func1(s string) (n int, err error) {
	defer func() {
		log.Printf("func1(%q) = %d, %v", s, n, err)
	}()
	return 7, io.EOF
}

func main() {
	func1("Go")
}
```

输出:

```
Output: 2011/10/04 10:46:11 func1("Go") = 7, EOF
```
