---
title: Struct Construction
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/struct/construction
---

## 工厂方法

```go
type File struct {
    fd      int     // 文件描述符
    name    string  // 文件名
}

func NewFile(fd int, name string) *File {
    if fd < 0 {
        return nil
    }

    return &File{fd, name}
}

f := NewFile(10, "./test.txt")
```

工厂方法像面向对象的语言那样实例化对象。可以用 `size := unsafe.Sizeof(T{})` 来查看一个实例占用了多少内存。

### 强制使用工厂方法

```go
type matrix struct {
    ...
}

// 仅仅暴露工厂方法
func NewMatrix(params) *matrix {
    m := new(matrix) // 初始化 m
    return m
}
```

## `make()` vs `new()`

+ `make()`返回对象值
+ `new()`返回指针

```go
package main

type Foo map[string]string
type Bar struct {
    thingOne string
    thingTwo int
}

func main() {
    // OK
    y := new(Bar)
    (*y).thingOne = "hello"
    (*y).thingTwo = 1

    // NOT OK
    z := make(Bar)  // 编译错误：cannot make type Bar
    (*z).thingOne = "hello"
    (*z).thingTwo = 1

    // OK
    x := make(Foo)
    x["x"] = "goodbye"
    x["y"] = "world"

    // NOT OK
    u := new(Foo)
    (*u)["x"] = "goodbye" // 运行时错误!! panic: assignment to entry in nil map
    (*u)["y"] = "world"
}
```

## 结构体 `tag`

```go
package main

import (
	"fmt"
	"reflect"
)

type User struct {
	Name     string `label:"用户名" required:"true" maxlen:"30"`
	Email    string `label:"电子邮件" required:"true" maxlen:"50"`
	Age      int    `label:"年龄" required:"false"`
	Location string `label:"地址" required:"false" maxlen:"100"`
}

func main() {
	user := User{
		Name:     "Alice",
		Email:    "alice@example.com",
		Age:      25,
		Location: "Wonderland",
	}
	printFieldTags(user)
}

// printFieldTags 函数通过反射读取结构体字段标签并打印标签信息
func printFieldTags(data interface{}) {
	val := reflect.ValueOf(data)
	typ := reflect.TypeOf(data)

	fmt.Printf("结构体 %s 的字段标签:\n", typ.Name())
	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)
		value := val.Field(i).Interface()

		label := field.Tag.Get("label")
		required := field.Tag.Get("required")
		maxlen := field.Tag.Get("maxlen")

		fmt.Printf("字段: %s\n", field.Name)
		fmt.Printf("  标签 - 名称: %s, 必填: %s, 最大长度: %s\n", label, required, maxlen)
		fmt.Printf("  当前值: %v\n\n", value)
	}
}
```

## 匿名字段

观察例子

```go
package main

import "fmt"

type innerS struct {
	in1 int
	in2 int
}

type outerS struct {
	b    int
	c    float32
	int  // anonymous field
	innerS //anonymous field
}

func main() {
	outer := new(outerS)
	outer.b = 6
	outer.c = 7.5
	outer.int = 60
	outer.in1 = 5
	outer.in2 = 10

	fmt.Printf("outer.b is: %d\n", outer.b)
	fmt.Printf("outer.c is: %f\n", outer.c)
	fmt.Printf("outer.int is: %d\n", outer.int)
	fmt.Printf("outer.in1 is: %d\n", outer.in1)
	fmt.Printf("outer.in2 is: %d\n", outer.in2)

	// 使用结构体字面量
	outer2 := outerS{6, 7.5, 60, innerS{5, 10}}
	fmt.Println("outer2 is:", outer2)
}
```

输出

```go
outer.b is: 6
outer.c is: 7.500000
outer.int is: 60
outer.in1 is: 5
outer.in2 is: 10
outer2 is:{6 7.5 60 {5 10}}
```

在一个结构体中对于每一种数据类型只能有一个匿名字段。

## 内嵌结构体

同样地结构体也是一种数据类型，所以它也可以作为一个匿名字段来使用，如同上面例子中那样。外层结构体通过 `outer.in1` 直接进入内层结构体的字段，内嵌结构体甚至可以来自其他包。内层结构体被简单的插入或者内嵌进外层结构体。这个简单的“继承”机制提供了一种方式，使得可以从另外一个或一些类型继承部分或全部实现。

```go
package main

import "fmt"

type A struct {
	ax, ay int
}

type B struct {
	A
	bx, by float32
}

func main() {
	b := B{A{1, 2}, 3.0, 4.0}
	fmt.Println(b.ax, b.ay, b.bx, b.by)
	fmt.Println(b.A)
}
```

### 命名冲突

当两个字段拥有相同的名字（可能是继承来的名字）时该怎么办呢？

1. 外层名字会覆盖内层名字（但是两者的内存空间都保留），这提供了一种重载字段或方法的方式；
2. 如果相同的名字在同一级别出现了两次，如果这个名字被程序使用了，将会引发一个错误（不使用没关系）。没有办法来解决这种问题引起的二义性，必须由程序员自己修正。

使用 `c.a` 是错误的，到底是 `c.A.a` 还是 `c.B.a` 呢？会导致编译器错误：**ambiguous DOT reference c.a disambiguate with either c.A.a or c.B.a**。

```go
type A struct {a int}
type B struct {a, b int}

type C struct {A; B}
var c C
```

使用 `d.b` 是没问题的：它是 float32，而不是 `B` 的 `b`。如果想要内层的 `b` 可以通过 `d.B.b` 得到。

```go
type D struct {B; b float32}
var d D
```