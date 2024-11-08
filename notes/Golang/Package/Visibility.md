---
title: Visibility
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/package/visibility/
---

## 概述

这里有个简单例子来说明包是如何相互调用以及可见性是如何实现的。

```go
package pack1
var Pack1Int int = 42 // 
var pack1Float = 3.14

func ReturnStr() string {
	return "Hello main!"
}
```

当标识符（包括常量、变量、类型、函数名、结构字段等等）以一个大写字母开头，如：Group1，那么使用这种形式的标识符的对象就可以被外部包的代码所使用（客户端程序需要先导入这个包），这被称为导出（像面向对象语言中的 public）；标识符如果以小写字母开头，则对包外是不可见的，但是他们在整个包的内部是可见并且可用的（像面向对象语言中的 private ）。

（大写字母可以使用任何 Unicode 编码的字符，比如希腊文，不仅仅是 ASCII 码中的大写字母）。

因此，在导入一个外部包后，能够且只能够访问该包中导出的对象。

```go
package main

import (
	"fmt"
	"./pack1"
)

func main() {
	var test1 string
	test1 = pack1.ReturnStr()
	fmt.Printf("ReturnStr from package1: %s\n", test1)
	fmt.Printf("Integer from package1: %d\n", pack1.Pack1Int)
	// fmt.Printf("Float from package1: %f\n", pack1.pack1Float)
}
```

### `import with .`

```go
import . "./pack1"
```

### `import with _`

```go
import _ "./pack1/pack1"
```

pack1包只导入其副作用，也就是说，只执行它的init函数并初始化其中的全局变量。

## 初始化

程序的执行开始于导入包，初始化 `main` 包然后调用 `main` 函数。

一个没有导入的包将通过分配初始值给所有的包级变量和调用源码中定义的包级 `init` 函数来初始化。一个包可能有多个 `init` 函数甚至在一个源码文件中。它们的执行是无序的。这是最好的例子来测定包的值是否只依赖于相同包下的其他值或者函数。

`init` 函数是不能被调用的。

导入的包在包自身初始化前被初始化，而一个包在程序执行中只能初始化一次。