---
title: IF Statement in Golang.
createTime: 2024-7-15
tags:
  - Golang
description: 笔记记录了Golang中的If语句。
---
<br> 笔记记录了Golang中的If语句。
<!-- more -->

## 初始化语句

if 可以包含一个初始化语句（如：给一个变量赋值）。这种写法具有固定的格式（在初始化语句后方必须加上分号）：

```Go
if initialization; condition {
	// do something
}
```

例如:

```Go
if val := 10; val > max {
	// do something
}
```

但要注意的是，使用简短方式 `:=` 声明的变量的作用域只存在于 if 结构中（在 if 结构的大括号之间，如果使用 if-else 结构则在 else 代码块中变量也会存在）。如果变量在 if 结构之前就已经存在，那么在 if 结构中，该变量原来的值会被隐藏。**最简单的解决方案就是不要在初始化语句中声明变量**

> commet : 有点脱裤子放屁了

## 测试多返回值函数的错误

o 语言的函数经常使用两个返回值来表示执行是否成功：返回某个值以及 true 表示成功；返回零值（或 nil）和 false 表示失败（第 4.4 节）。当不使用 true 或 false 的时候，也可以使用一个 error 类型的变量来代替作为第二个返回值：成功执行的话，error 的值为 nil，否则就会包含相应的错误信息（Go 语言中的错误类型为 error: `var err error`，我们将会在第 13 章进行更多地讨论）。这样一来，就很明显需要用一个 if 语句来测试执行结果；由于其符号的原因，这样的形式又称之为 comma,ok 模式（pattern）。

在第 4.7 节的程序 `string_conversion.go` 中，函数 `strconv.Atoi` 的作用是将一个字符串转换为一个整数。之前我们忽略了相关的错误检查：

```Go
anInt, _ = strconv.Atoi(origStr)
```

如果 origStr 不能被转换为整数，anInt 的值会变成 0 而 `_` 无视了错误，程序会继续运行。

这样做是非常不好的：程序应该在最接近的位置检查所有相关的错误，至少需要暗示用户有错误发生并对函数进行返回，甚至中断程序。

我们在第二个版本中对代码进行了改进：

```Go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	var orig string = "ABC"
	// var an int
	var newS string
	// var err error

	fmt.Printf("The size of ints is: %d
", strconv.IntSize)	  
	// anInt, err = strconv.Atoi(origStr)
	an, err := strconv.Atoi(orig)
	if err != nil {
		fmt.Printf("orig %s is not an integer - exiting with error
", orig)
		return
	} 
	fmt.Printf("The integer is %d
", an)
	an = an + 5
	newS = strconv.Itoa(an)
	fmt.Printf("The new string is: %s
", newS)
}
```

这是测试 err 变量是否包含一个真正的错误（`if err != nil`）的习惯用法。如果确实存在错误，则会打印相应的错误信息然后通过 return 提前结束函数的执行。我们还可以使用携带返回值的 return 形式，例如 `return err`。这样一来，函数的调用者就可以检查函数执行过程中是否存在错误了

**习惯用法**

```Go
value, err := pack1.Function1(param1)
if err != nil {
	fmt.Printf("An error occured in pack1.Function1 with parameter %v", param1)
	return err
}
```

如果我们想要在错误发生的同时终止程序的运行，我们可以使用 `os` 包的 `Exit` 函数：

**习惯用法**

```Go
if err != nil {
	fmt.Printf("Program stopping with error %v", err)
	os.Exit(1)
}
```

可以将错误的获取放置在 if 语句的初始化部分：

**习惯用法**

```Go
if err := file.Chmod(0664); err != nil {
	fmt.Println(err)
	return err
}
```

或者将 ok-pattern 的获取放置在 if 语句的初始化部分，然后进行判断：

```Go
if value, ok := readData(); ok {
…
}
```

**注意事项**

如果您像下面一样，没有为多返回值的函数准备足够的变量来存放结果：

```Go
func mySqrt(f float64) (v float64, ok bool) {
	if f < 0 { return } // error case
	return math.Sqrt(f),true
}

func main() {
	t := mySqrt(25.0)
	fmt.Println(t)
}
```

会得到一个编译错误：`multiple-value mySqrt() in single-value context`。

```Go
t, ok := mySqrt(25.0)
if ok { fmt.Println(t) }
```

当您将字符串转换为整数时，且确定转换一定能够成功时，可以将 `Atoi` 函数进行一层忽略错误的封装：

```Go
func atoi (s string) (n int) {
	n, _ = strconv.Atoi(s)
	return
}
```

实际上，`fmt` 包（第 4.4.3 节）最简单的打印函数也有 2 个返回值：

```Go
count, err := fmt.Println(x) // number of bytes printed, nil or 0, error
```
