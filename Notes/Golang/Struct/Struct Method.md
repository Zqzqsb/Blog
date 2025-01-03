---
title: Struct Method
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/struct/method/
---

## 概述

方法是结构体的专属函数，或者说是面向对象概念中类的成员函数。当然，不仅仅是结构体，也可以是其他任意方法的接收者类型(receiver)。

最后接收者不能是一个指针类型，但是它可以是任何其他允许类型的指针。

因为方法是函数，所以同样的，不允许方法重载，即对于一个类型只能有一个给定名称的方法。但是如果基于接收者类型，是有重载的：具有同样名字的方法可以在 2 个或多个不同的接收者类型上存在，比如在同一个包里这么做是允许的：

```go
func (a *denseMatrix) Add(b Matrix) Matrix
func (a *sparseMatrix) Add(b Matrix) Matrix
```

定义方法的一般格式如下：

```go
func (recv receiver_type) methodName(parameter_list) (return_value_list) { ... }
```

`recv` 就像是面向对象语言中的 `this` 或 `self`，但是 Go 中并没有这两个关键字。随个人喜好，可以使用 `this` 或 `self` 作为 receiver 的名字。下面是一个结构体上的简单方法的例子：

## 定义

```go
package main

import "fmt"

type TwoInts struct {
	a int
	b int
}

func main() {
	two1 := new(TwoInts)
	two1.a = 12
	two1.b = 10

	fmt.Printf("The sum is: %d\n", two1.AddThem())
	fmt.Printf("Add them to the param: %d\n", two1.AddToParam(20))

	two2 := TwoInts{3, 4}
	fmt.Printf("The sum is: %d\n", two2.AddThem())
}

func (tn *TwoInts) AddThem() int {
	return tn.a + tn.b
}

func (tn *TwoInts) AddToParam(param int) int {
	return tn.a + tn.b + param
}
```

所有的方法的同一个本地包内定义。

但是有一个间接的方式：可以先定义该类型（比如：int 或 float）的别名类型，然后再为别名类型定义方法。或者像下面这样将它作为匿名类型嵌入在一个新的结构体中。当然方法只在这个别名类型上有效。

```go
package main

import (
	"fmt"
	"time"
)

type myTime struct {
	time.Time //anonymous field
}

func (t myTime) first3Chars() string {
	return t.Time.String()[0:3]
}
func main() {
	m := myTime{time.Now()}
	// 调用匿名Time上的String方法
	fmt.Println("Full time now:", m.String())
	// 调用myTime.first3Chars
	fmt.Println("First 3 chars:", m.first3Chars())
}

/* Output:
Full time now: Mon Oct 24 15:34:54 Romance Daylight Time 2011
First 3 chars: Mon
*/
```

## 参数传递

型 `List` 在值上有一个方法 `Len()`，在指针上有一个方法 `Append()`，两个方法都可以在两种类型的变量上被调用。

```go
package main

import (
	"fmt"
)

type List []int

func (l List) Len() int        { return len(l) }
func (l *List) Append(val int) { *l = append(*l, val) }

func main() {
	// 值
	var lst List
	lst.Append(1)
	fmt.Printf("%v (len: %d)", lst, lst.Len()) // [1] (len: 1)

	// 指针
	plst := new(List)
	plst.Append(2)
	fmt.Printf("%v (len: %d)", plst, plst.Len()) // &[2] (len: 1)
}
```

因为 `Append` 方法接收的是 `*List`，所以 Go 会**自动将 `lst` 的地址传递**给 `Append` 方法（即隐式地传递 `&lst`）。

## 封装性

结合 `package`的导出特点，可以实现类似 `getter` 和 `setter`的效果。

**并发访问对象**

对象的字段（属性）不应该由 2 个或 2 个以上的不同线程在同一时间去改变。如果在程序发生这种情况，为了安全并发访问，可以使用包 `sync`中的方法。


## 继承

当一个匿名类型被内嵌在结构体中时，匿名类型的可见方法也同样被内嵌，这在效果上等同于外层类型 **继承** 了这些方法：**将父类型放在子类型中来实现亚型**。这个机制提供了一种简单的方式来模拟经典面向对象语言中的子类和继承相关的效果。

```go
type Engine interface {
	Start()
	Stop()
}

type Car struct {
	Engine
}
```

我们可以构建如下的代码：

```go
func (c *Car) GoToWorkIn() {
	// get in car
	c.Start()
	// drive to work
	c.Stop()
	// get out of car
}
```

再看一个更加完整的例子

```go
package main

import (
	"fmt"
	"math"
)

type Point struct {
	x, y float64
}

func (p *Point) Abs() float64 {
	return math.Sqrt(p.x*p.x + p.y*p.y)
}

type NamedPoint struct {
	Point
	name string
}

func main() {
	n := &NamedPoint{Point{3, 4}, "Pythagoras"}
	fmt.Println(n.Abs()) // 打印5
}
```

## 封装复杂的功能

```go
package main

import (
	"fmt"
)

type Log struct {
	msg string
}

type Customer struct {
	Name string
	log  *Log
}

func main() {
	c := new(Customer)
	c.Name = "Barak Obama"
	c.log = new(Log)
	c.log.msg = "1 - Yes we can!"
	// shorter
	c = &Customer{"Barak Obama", &Log{"1 - Yes we can!"}}
	// fmt.Println(c) &{Barak Obama 1 - Yes we can!}
	c.Log().Add("2 - After me the world will be a better place!")
	//fmt.Println(c.log)
	fmt.Println(c.Log())

}

func (l *Log) Add(s string) {
	l.msg += "\n" + s
}

func (l *Log) String() string {
	return l.msg
}

func (c *Customer) Log() *Log {
	return c.log
}
```

## 多重继承

通过嵌入多个必要的类型来实现多重继承。

```go
package main

import (
	"fmt"
)

type Camera struct{}

func (c *Camera) TakeAPicture() string {
	return "Click"
}

type Phone struct{}

func (p *Phone) Call() string {
	return "Ring Ring"
}

type CameraPhone struct {
	Camera
	Phone
}

func main() {
	cp := new(CameraPhone)
	fmt.Println("Our new CameraPhone exhibits multiple behaviors...")
	fmt.Println("It exhibits behavior of a Camera: ", cp.TakeAPicture())
	fmt.Println("It works like a Phone too: ", cp.Call())
}
```

## 格式化输出

当定义了一个有很多方法的类型时，十之八九你会使用 `String()` 方法来定制类型的字符串形式的输出，换句话说：一种可阅读性和打印性的输出。如果类型定义了 `String()` 方法，它会被用在 `fmt.Printf()` 中生成默认的输出：等同于使用格式化描述符 `%v` 产生的输出。

```go
package main

import (
	"fmt"
	"strconv"
)

type TwoInts struct {
	a int
	b int
}

func main() {
	two1 := new(TwoInts)
	two1.a = 12
	two1.b = 10
	fmt.Printf("two1 is: %v\n", two1)
	fmt.Println("two1 is:", two1)
	fmt.Printf("two1 is: %T\n", two1)
	fmt.Printf("two1 is: %#v\n", two1)
}

func (tn *TwoInts) String() string {
	return "(" + strconv.Itoa(tn.a) + "/" + strconv.Itoa(tn.b) + ")"
}
```

```go
two1 is: (12/10)
two1 is: (12/10)
two1 is: *main.TwoInts
two1 is: &main.TwoInts{a:12, b:10}
```