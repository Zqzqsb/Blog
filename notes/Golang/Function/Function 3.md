---
title: Functions in Golang Chapter3.
createTime: 2024-7-17
tags:
  - Golang
description: 笔记记录了Golang中的函数。
---
<br> 笔记记录了Golang中的函数。
<!-- more -->

## 内置函数

Go 语言拥有一些不需要进行导入操作就可以使用的内置函数。它们有时可以针对不同的类型进行操作，例如：len、cap 和 append，或必须用于系统级的操作，例如：panic。因此，它们需要直接获得编译器的支持。

以下是一个简单的列表，我们会在后面的章节中对它们进行逐个深入的讲解。

| 名称                | 说明                                                                                                                                                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| close             | 用于管道通信                                                                                                                                                                                                                                   |
| len、cap           | len 用于返回某个类型的长度或数量（字符串、数组、切片、map 和管道）；cap 是容量的意思，用于返回某个类型的最大容量（只能用于切片和 map）                                                                                                                                                              |
| new、make          | new 和 make 均是用于分配内存：new 用于值类型和用户定义的类型，如自定义结构，make 用于内置引用类型（切片、map 和管道）。它们的用法就像是函数，但是将类型作为参数：new(type)、make(type)。new(T) 分配类型 T 的零值并返回其地址，也就是指向类型 T 的指针（详见第 10.1 节）。它也可以被用于基本类型：`v := new(int)`。make(T) 返回类型 T 的初始化之后的值，因此它比 new 进行更多的工作。 |
| copy、append       | 用于复制和连接切片                                                                                                                                                                                                                                |
| panic、recover     | 两者均用于错误处理机制                                                                                                                                                                                                                              |
| print、println     | 底层打印函数，在部署环境中建议使用 fmt 包                                                                                                                                                                                                                  |
| complex、real imag | 用于创建和操作复数。                                                                                                                                                                                                                               |

## 将函数作为参数

函数可以作为其它函数的参数进行传递，然后在其它函数内调用执行，一般称之为回调。下面是一个将函数作为参数的简单例子（function_parameter.go）：

```go
package main

import (
	"fmt"
)

func main() {
	callback(1, Add)
}

func Add(a, b int) {
	fmt.Printf("The sum of %d and %d is: %d
", a, b, a+b)
}

func callback(y int, f func(int, int)) {
	f(y, 2) // this becomes Add(1, 2)
}
```

输出：

```
The sum of 1 and 2 is: 3
```

>  为什么不需要指定函数的返回类型？ 我猜想函数签名本身就被认为是一种类型。

将函数作为参数的最好的例子是函数 `strings.IndexFunc()`：

该函数的签名是 `func IndexFunc(s string, f func(c rune) bool) int`，它的返回值是在函数 `f(c)` 返回 true、-1 或从未返回时的索引值。

例如 `strings.IndexFunc(line, unicode.IsSpace)` 就会返回 `line` 中第一个空白字符的索引值。当然，您也可以书写自己的函数：

```go
func IsAscii(c int) bool {
	if c > 255 {
		return false
	}
	return true
}
```

## 闭包

当我们不希望给函数起名字的时候，可以使用匿名函数，例如：`func(x, y int) int { return x + y }`。

这样的一个函数不能够独立存在（编译器会返回错误：`non-declaration statement outside function body`），但可以被赋值于某个变量，即保存函数的地址到变量中：`fplus := func(x, y int) int { return x + y }`，然后通过变量名对函数进行调用：`fplus(3,4)`。

当然，您也可以直接对匿名函数进行调用：`func(x, y int) int { return x + y } (3, 4)`。

下面是一个计算从 1 到 1 百万整数的总和的匿名函数

```go
func() {
	sum := 0
	for i := 1; i <= 1e6; i++ {
		sum += i
	}
}()
```

表示参数列表的第一对括号必须紧挨着关键字 `func`，因为匿名函数没有名称。花括号 `{}` 涵盖着函数体，最后的一对括号表示对该匿名函数的调用。

下面的例子展示了如何将匿名函数赋值给变量并对其进行调用:

```go
package main

import "fmt"

func main() {
	f()
}
func f() {
	for i := 0; i < 4; i++ {
		g := func(i int) { fmt.Printf("%d ", i) } //此例子中只是为了演示匿名函数可分配不同的内存地址，在现实开发中，不应该把该部分信息放置到循环中。
		g(i)
		fmt.Printf(" - g is of type %T and has value %v
", g, g)
	}
}
```

输出：

```
0 - g is of type func(int) and has value 0x681a80
1 - g is of type func(int) and has value 0x681b00
2 - g is of type func(int) and has value 0x681ac0
3 - g is of type func(int) and has value 0x681400
```

我们可以看到变量 `g` 代表的是 `func(int)`，变量的值是一个内存地址。

所以我们实际上拥有的是一个函数值：匿名函数可以被赋值给变量并作为值使用。

##  应用闭包

```
func Add2() (func(b int) int)
func Adder(a int) (func(b int) int)
```

函数 Add2 不接受任何参数，但函数 Adder 接受一个 int 类型的整数作为参数。

我们也可以将 Adder 返回的函数存到变量中（function_return.go）。

```go
package main

import "fmt"

func main() {
	// make an Add2 function, give it a name p2, and call it:
	p2 := Add2()
	fmt.Printf("Call Add2 for 3 gives: %v
", p2(3))
	// make a special Adder function, a gets value 2:
	TwoAdder := Adder(2)
	fmt.Printf("The result is: %v
", TwoAdder(3))
}

func Add2() func(b int) int {
	return func(b int) int {
		return b + 2
	}
}

func Adder(a int) func(b int) int {
	return func(b int) int {
		return a + b
	}
}
```

>  和匿名函数的定义区分开来

+ 这是将函数执行的返回值赋值给变量， 此时函数的返回值是另一个函数签名。
+ 函数过程并没有发生， 而是在使用变量时发生了类似链式调用的过程。
+ 调用时使用的函数返回函数的参数

```go
func main() {
	p2 := Add2()
	p2(3)
}

func Add2() func(b int) int {
	return func(b int) int {
		return b + 2
	}
}
```

+ 这是在定义一个匿名函数，并且将它绑定到某个变量上。
+ 调用时使用的函数本身的参数
+ 可以打印 `p2` 和 `g`的类型进行比较

```go
	g := func(i int) { fmt.Printf("%d ", i) }
	g(i)
```

## 使用闭包调试

当在分析和调试复杂的程序时，无数个函数在不同的代码文件中相互调用，如果这时候能够准确地知道哪个文件中的具体哪个函数正在执行，对于调试是十分有帮助的。您可以使用 `runtime` 或 `log` 包中的特殊函数来实现这样的功能。包 `runtime` 中的函数 `Caller()` 提供了相应的信息，因此可以在需要的时候实现一个 `where()` 闭包函数来打印函数执行的位置：

```go
where := func() {
	_, file, line, _ := runtime.Caller(1)
	log.Printf("%s:%d", file, line)
}
where()
// some code
where()
// some more code
where()
```

```go
log.SetFlags(log.Llongfile)
log.Print("")
```

```go
var where = log.Print
func func1() {
where()
... some code
where()
... some code
where()
}
```
