---
title: Concept about Interface in Golang.
createTime: 2024-11-13
tags:
  - Golang
description: 笔记记录了Golang中的接口。
permalink: /note/golang/interface/concept/
---

## 概述

Go 语言不是一种 “传统” 的面向对象编程语言：它里面没有类和继承的概念。

但是 Go 语言里有非常灵活的 **接口** 概念，通过它可以实现很多面向对象的特性。接口提供了一种方式来 **说明** 对象的行为：如果谁能搞定这件事，它就可以用在这儿。

接口定义了一组方法（方法集），但是这些方法不包含（实现）代码：它们没有被实现（它们是抽象的）。接口里也不能包含变量。

```go
type Namer interface {
    Method1(param_list) return_type
    Method2(param_list) return_type
    ...
}
```

在 Go 语言中接口可以有值，一个接口类型的变量或一个 **接口值** ：`var ai Namer`，`ai` 是一个多字（multiword）数据结构，它的值是 `nil`。它本质上是一个指针，虽然不完全是一回事。`ai`指向两个域,`receiver`和`receiver`所实现的`method table`。

> 指向接口值的指针是非法的，它们不仅一点用也没有，还会导致代码错误。

类型（比如结构体）可以实现某个接口的方法集；这个实现可以描述为，该类型的变量上的每一个具体方法所组成的集合，包含了该接口的方法集。实现了 `Namer` 接口的类型的变量可以赋值给 `ai`（即 `receiver` 的值），方法表指针（method table ptr）就指向了当前的方法实现。当另一个实现了 `Namer` 接口的类型的变量被赋给 `ai`，`receiver` 的值和方法表指针也会相应改变。

## 实现规则

1. **类型不需要显式声明它实现了某个接口：接口被隐式地实现。多个类型可以实现同一个接口**。
2. **实现某个接口的类型（除了实现接口方法外）可以有其他的方法**。
3. **一个类型可以实现多个接口**。
4. **接口类型可以包含一个实例的引用， 该实例的类型实现了此接口（接口是动态类型）**。
5. **即使接口在类型之后才定义，二者处于不同的包中，被单独编译：只要类型实现了接口中的方法，它就实现了此接口。**

## 例子

**例子一**

```go
package main

import "fmt"

type Shaper interface {
	Area() float32
}

type Square struct {
	side float32
}

func (sq *Square) Area() float32 {
	return sq.side * sq.side
}

func main() {
	sq1 := new(Square)
	sq1.side = 5

	var areaIntf Shaper
	areaIntf = sq1
	// shorter,without separate declaration:
	// areaIntf := Shaper(sq1)
	// or even:
	// areaIntf := sq1
	fmt.Printf("The square has area: %f\n", areaIntf.Area())
}
```

**例子二**

`io` 包里有一个接口类型 `Reader`:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

```go
var r io.Reader
	r = os.Stdin
	r = bufio.NewReader(r)
	r = new(bytes.Buffer)
	f,_ := os.Open("test.txt")
	r = bufio.NewReader(f)
```

上面 `r` 右边的类型都实现了 `Read()` 方法，并且有相同的方法签名，`r` 的静态类型是 `io.Reader`。

> 有的时候，也会以一种稍微不同的方式来使用接口这个词：从某个类型的角度来看，它的接口指的是：它的所有导出方法，只不过没有显式地为这些导出方法额外定一个接口而已。

## 嵌套接口

一个接口可以包含一个或多个其他的接口，这相当于直接将这些内嵌接口的方法列举在外层接口中一样。

```go
type ReadWrite interface {
    Read(b Buffer) bool
    Write(b Buffer) bool
}
type Lock interface {
    Lock()
    Unlock()
}
type File interface {
    ReadWrite
    Lock
    Close()
}
```

## 类型断言

一个接口类型的变量 `varI` 中可以包含任何类型的值，必须有一种方式来检测它的 **动态** 类型，即运行时在变量中存储的值的实际类型。在执行过程中动态类型可能会有所不同，但是它总是可以分配给接口变量本身的类型。通常我们可以使用 **类型断言** 来测试在某个时刻 `varI` 是否包含类型 `T` 的值：

```go
v := varI.(T)
```

**更加防御性的编程**

```go
if _, ok := varI.(T); ok {  // checked type assertion
    Process(v)
    return
}
// varI is not of type T
```

如果转换合法，`v` 是 `varI` 转换到类型 `T` 的值，`ok` 会是 `true`；否则 `v` 是类型 `T` 的零值，`ok` 是 `false`，也没有运行时错误发生。

### `typeswitch`

```go
switch t := areaIntf.(type) {
	case *Square:
		fmt.Printf("Type Square %T with value %v\n", t, t)
	case *Circle:
		fmt.Printf("Type Circle %T with value %v\n", t, t)
	case nil:
		fmt.Printf("nil value: nothing to check?\n")
	default:
		fmt.Printf("Unexpected type %T\n", t)
}
```

###  测试类型是否实现了接口

使用相同的语法测试某个类型是否实现接口

```go
type Stringer interface {
    String() string
}
if sv, ok := v.(Stringer); ok {
    fmt.Printf("v implements String(): %s\n", sv.String()) // note: sv, not v
}
```

## 引用类型

作用于变量上的方法实际上是不区分变量到底是指针还是值的。当碰到接口类型值时，这会变得有点复杂，原因是接口变量中存储的具体值是不可寻址。

```go
package main
import (
	"fmt"
)
type List []int
func (l List) Len() int {
	return len(l)
}
func (l *List) Append(val int) {
	*l = append(*l, val)
}
type Appender interface {
	Append(int)
}
func CountInto(a Appender, start, end int) {
	for i := start; i <= end; i++ {
		a.Append(i)
	}
}
type Lener interface {
	Len() int
}
func LongEnough(l Lener) bool {
	return l.Len()*10 > 42
}
func main() {
	// A bare value
	var lst List
	
	// CountInto(lst, 1, 10)
	// compiler error:
	// cannot use lst (type List) as type Appender in argument to CountInto:
	//       List does not implement Appender (Append method has pointer receiver)
	
	if LongEnough(lst) { // VALID:Identical receiver type
		fmt.Printf("- lst is long enough\n")
	}
	// A pointer value
	plst := new(List)
	CountInto(plst, 1, 10) //VALID:Identical receiver type
	if LongEnough(plst) {
		// VALID: a *List can be dereferenced for the receiver
		fmt.Printf("- plst is long enough\n")
	}
}
```

**讨论**

在 `lst` 上调用 `CountInto` 时会导致一个编译器错误，因为 `CountInto` 需要一个 `Appender`，而它的方法 `Append` 只定义在指针上。 在 `lst` 上调用 `LongEnough` 是可以的，因为 `Len` 定义在值上。

在 `plst` 上调用 `CountInto` 是可以的，因为 `CountInto` 需要一个 `Appender`，并且它的方法 `Append` 定义在指针上。 在 `plst` 上调用 `LongEnough` 也是可以的，因为指针会被自动解引用。

**总结**

在接口上调用方法时，必须有和方法定义时相同的接收者类型或者是可以从具体类型 `P` 直接可以辨识的：

- 指针方法可以通过指针调用
- 值方法可以通过值调用
- 接收者是值的方法可以通过指针调用，因为指针会首先被解引用
- 接收者是指针的方法不可以通过值调用，因为存储在接口中的值没有地址

将一个值赋值给一个接口时，编译器会确保所有可能的接口方法都可以在此值上被调用，因此不正确的赋值在编译期就会失败。Go 语言中，**方法集**（Method Set）定义了一个类型可以调用哪些方法。方法接收者的类型决定了哪些方法属于类型的方法集。

> Go 语言规范定义了接口方法集的调用规则：

- 类型 T 的可调用方法集包含接受者为 \*T 或 T 的所有方法集
- 类型 \*T 的可调用方法集包含接受者为 \*T 的所有方法
- 类型 \*T 的可调用方法集不包含接受者为 T 的方法

