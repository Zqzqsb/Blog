---
title: Struct Basic
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/struct/basic/
---

## 概述

Go 通过类型别名（alias types）和结构体的形式支持用户自定义类型，或者叫定制类型。

结构体也是值类型，因此可以通过 `new` 函数来创建。

> 结构体的概念在软件工程上旧的术语叫 ADT（抽象数据类型：Abstract Data Type) , 在 C 家族的编程语言中它也存在，并且名字也是 **struct**，在面向对象的编程语言中，跟一个无方法的轻量级类一样。不过因为 Go 语言中没有类的概念，因此在 Go 中结构体有着更为重要的地位。

## 定义和创建

结构体定义的一般方式如下：

```go
type identifier struct {
    field1 type1
    field2 type2
    ...
}
```

结构体里的字段都有 **名字**，像 field1、field2 等，如果字段在代码中从来也不会被用到，那么可以命名它为 `_`。

** 结构体的字段可以是任何类型，甚至是结构体本身，也可以是函数或者接口。**

`type T struct {a, b int}` 也是合法的语法，它更适用于简单的结构体。可以声明结构体类型的一个变量，然后像下面这样给它的字段赋值：

```go
var s T
s.a = 5
s.b = 8
```

数组可以看作是一种结构体类型，不过它使用下标而不是具名的字段。
### 使用 `new`

使用 **new** 函数给一个新的结构体变量分配内存，它返回指向已分配内存的指针：`var t *T = new(T)`。

```go
var t *T
t = new(T)
```

变量 `t` 是一个指向 `T`的指针，此时结构体字段的值是它们所属类型的零值。

> 声明 `var t T` 也会给 `t` 分配内存，并零值化内存，但是这个时候 `t` 是类型T。

### 混合字面量语法

```go
 ms := &struct1{10, 15.5, "Chris"} // 此时ms的类型是 *struct1
```

```go 
var ms struct1
    ms = struct1{10, 15.5, "Chris"} // 此时ms的类型是 struct1
```

混合字面量语法（composite literal syntax）`&struct1{a, b, c}` 是一种简写，底层仍然会调用 `new ()`，这里值的顺序必须按照字段顺序来写。在下面的例子中能看到可以通过在值的前面放上字段名来初始化字段的方式。表达式 `new(Type)` 和 `&Type{}` 是等价的。

```go
intr := Interval{0, 3}            (A)
intr := Interval{end:5, start:1}  (B)
intr := Interval{end:5}           (C)
```

在（A）中，值必须以字段在结构体定义时的顺序给出, `&` 不是必须的。（B）显示了另一种方式，字段名加一个冒号放在值的前面，这种情况下值的顺序不必一致，并且某些字段还可以被忽略掉，就像（C）中那样。
### 内存分配

两者的内存分配位置在 Go 中并不明确，因为 Go 会根据需要自动决定是否在堆上分配内存。不过，在语义上：

- `new(T)`用于需要获取指向类型 `T` 的指针的场景。通常更适合需要共享或修改同一个结构体实例的场景。
- `var t T`用于直接使用类型 `T` 的值，而无需通过指针访问。

**使用`new`**

获得一个指针类型

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Notes/golang/InitWithNew.png)

**使用混合字面量**

是否使用引用符号决定是否获得一个指针类型

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Notes/golang/InitWithIter.png)

Go 语言中，结构体和它所包含的数据在内存中是以连续块的形式存在的，即使结构体中嵌套有其他的结构体，这在性能上带来了很大的优势。不像 Java 中的引用类型，一个对象和它里面包含的对象可能会在不同的内存空间中，这点和 Go 语言中的指针很像。下面的例子清晰地说明了这些情况

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Notes/golang/ContinualMemoryAllocation.png)


## 使用

### 赋值取值

就像在面向对象语言所作的那样，可以使用点号符给字段赋值：`structname.fieldname = value`。同样的，使用点号符可以获取结构体字段的值：`structname.fieldname`。

在 Go 语言中这叫 **选择器（selector）**。无论变量是一个结构体类型还是一个结构体类型指针，都使用同样的 **选择器符（selector-notation）** 来引用结构体的字段：

```go
type myStruct struct { i int }
var v myStruct    // v是结构体类型变量
var p *myStruct   // p是指向一个结构体类型变量的指针
v.i
p.i
```

```go
package main
import (
    "fmt"
    "strings"
)

type Person struct {
    firstName   string
    lastName    string
}

func upPerson(p *Person) {
    p.firstName = strings.ToUpper(p.firstName)
    p.lastName = strings.ToUpper(p.lastName)
}

func main() {
    // 1-struct as a value type:
    var pers1 Person
    pers1.firstName = "Chris"
    pers1.lastName = "Woodward"
    upPerson(&pers1)
    fmt.Printf("The name of the person is %s %s\n", pers1.firstName, pers1.lastName)

    // 2—struct as a pointer:
    pers2 := new(Person)
    pers2.firstName = "Chris"
    pers2.lastName = "Woodward"
    (*pers2).lastName = "Woodward"  // 这是合法的
    upPerson(pers2)
    fmt.Printf("The name of the person is %s %s\n", pers2.firstName, pers2.lastName)

    // 3—struct as a literal:
    pers3 := &Person{"Chris","Woodward"}
    upPerson(pers3)
    fmt.Printf("The name of the person is %s %s\n", pers3.firstName, pers3.lastName)
}
```

在上面例子的第二种情况中，可以直接通过指针，像 `pers2.lastName="Woodward"` 这样给结构体字段赋值，没有像 C++ 中那样需要使用 `->` 操作符，Go 会自动做这样的转换。

注意也可以通过解指针的方式来设置值：`(*pers2).lastName = "Woodward"`

### 递归结构体

和`C`中的写法很类似，不赘述。例子定义二叉树的一个节点。

```go
type Node struct {
    pr      *Node
    data    float64
    su      *Node
}
```