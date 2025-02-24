---
title: Package Intro
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/package/intro/
---

## 概述

包是结构化代码的一种方式：每个程序都由包（通常简称为 pkg）的概念组成，可以使用自身的包或者从其它包中导入内容。

如同其它一些编程语言中的类库或命名空间的概念，每个 Go 文件都属于且仅属于一个包。一个包可以由许多以 `.go` 为扩展名的源文件组成，因此文件名和包名一般来说都是不相同的。

你必须在源文件中非注释的第一行指明这个文件属于哪个包，如：`package main`。`package main`表示一个可独立执行的程序，每个 Go 应用程序都包含一个名为 `main` 的包。

一个应用程序可以包含不同的包，而且即使你只使用 main 包也不必把所有的代码都写在一个巨大的文件里：你可以用一些较小的文件，并且在每个文件非注释的第一行都使用 `package main` 来指明这些文件都属于 main 包。如果你打算编译包名不是为 main 的源文件，如 `pack1`，编译后产生的对象文件将会是 `pack1.a` 而不是可执行程序。另外要注意的是，所有的包名都应该使用小写字母。

## 包的构建

如果想要构建一个程序，则包和包内的文件都必须以正确的顺序进行编译。包的依赖关系决定了其构建顺序。属于同一个包的源文件必须全部被一起编译，一个包即是编译时的一个单元，因此根据惯例，每个目录都只包含一个包。

**如果对一个包进行更改或重新编译，所有引用了这个包的客户端程序都必须全部重新编译。**

Go 中的包模型采用了显式依赖关系的机制来达到快速编译的目的，编译器会从后缀名为 `.o` 的对象文件（需要且只需要这个文件）中提取传递依赖类型的信息。

如果 `A.go` 依赖 `B.go`，而 `B.go` 又依赖 `C.go`：

- 编译 `C.go`, `B.go`, 然后是 `A.go`.
- 为了编译 `A.go`, 编译器读取的是 `B.o` 而不是 `C.o`.

这种机制对于编译大型的项目时可以显著地提升编译速度。

## 标准库

在 Go 的安装文件里包含了一些可以直接使用的包，即标准库。在 Windows 下，标准库的位置在 Go 根目录下的子目录 `pkg\windows_386` 中；在 Linux 下，标准库在 Go 根目录下的子目录 `pkg\linux_amd64` 中（如果是安装的是 32 位，则在 `linux_386` 目录中）。一般情况下，标准包会存放在 `$GOROOT/pkg/$GOOS_$GOARCH/` 目录下。

像 `fmt`、`os` 等这样具有常用功能的内置包在 Go 语言中有 150 个以上，它们被称为标准库，大部分(一些底层的除外)内置于 Go 本身。完整列表可以在 [Go Walker](https://gowalker.org/search?q=gorepos)查看。

比如

- `unsafe`: 包含了一些打破 Go 语言“类型安全”的命令，一般的程序中不会被使用，可用在 C/C++ 程序的调用中。
- `syscall`-`os`-`os/exec`:
    - `os`: 提供给我们一个平台无关性的操作系统功能接口，采用类Unix设计，隐藏了不同操作系统间差异，让不同的文件系统和操作系统对象表现一致。
    - `os/exec`: 提供我们运行外部操作系统命令和程序的方式。
    - `syscall`: 底层的外部包，提供了操作系统底层调用的基本接口。

通过一个 Go 程序让Linux重启来体现它的能力。

```go
package main
import (
	"syscall"
)

const LINUX_REBOOT_MAGIC1 uintptr = 0xfee1dead
const LINUX_REBOOT_MAGIC2 uintptr = 672274793
const LINUX_REBOOT_CMD_RESTART uintptr = 0x1234567

func main() {
	syscall.Syscall(syscall.SYS_REBOOT,
		LINUX_REBOOT_MAGIC1,
		LINUX_REBOOT_MAGIC2,
		LINUX_REBOOT_CMD_RESTART)
}
```

- `archive/tar` 和 `/zip-compress`：压缩(解压缩)文件功能。
- `fmt`-`io`-`bufio`-`path/filepath`-`flag`:
    - `fmt`: 提供了格式化输入输出功能。
    - `io`: 提供了基本输入输出功能，大多数是围绕系统功能的封装。
    - `bufio`: 缓冲输入输出功能的封装。
    - `path/filepath`: 用来操作在当前系统中的目标文件名路径。
    - `flag`: 对命令行参数的操作。
- `strings`-`strconv`-`unicode`-`regexp`-`bytes`:
    - `strings`: 提供对字符串的操作。
    - `strconv`: 提供将字符串转换为基础类型的功能。
    - `unicode`: 为 unicode 型的字符串提供特殊的功能。
    - `regexp`: 正则表达式功能。
    - `bytes`: 提供对字符型分片的操作。
    - `index/suffixarray`: 子字符串快速查询。
- `math`-`math/cmath`-`math/big`-`math/rand`-`sort`:
    - `math`: 基本的数学函数。
    - `math/cmath`: 对复数的操作。
    - `math/rand`: 伪随机数生成。
    - `sort`: 为数组排序和自定义集合。
    - `math/big`: 大数的实现和计算。
- `container`-`/list-ring-heap`: 实现对集合的操作。
    - `list`: 双链表。
    - `ring`: 环形链表。

下面代码演示了如何遍历一个链表(当 l 是 `*List`)：

```go
for e := l.Front(); e != nil; e = e.Next() {
	//do something with e.Value
}
```

- `time`-`log`:
    - `time`: 日期和时间的基本操作。
    - `log`: 记录程序运行时产生的日志,我们将在后面的章节使用它。
- `encoding/json`-`encoding/xml`-`text/template`:
    - `encoding/json`: 读取并解码和写入并编码 JSON 数据。
    - `encoding/xml`:简单的 XML1.0 解析器,有关 JSON 和 XML 的实例请查阅第 12.9/10 章节。
    - `text/template`:生成像 HTML 一样的数据与文本混合的数据驱动模板（参见第 15.7 节）。
- `net`-`net/http`-`html`:（参见第 15 章）
    - `net`: 网络数据的基本操作。
    - `http`: 提供了一个可扩展的 HTTP 服务器和基础客户端，解析 HTTP 请求和回复。
    - `html`: HTML5 解析器。
- `runtime`: Go 程序运行时的交互操作，例如垃圾回收和协程创建。
- `reflect`: 实现通过程序运行时反射，让程序操作任意类型的变量。

`exp` 包中有许多将被编译为新包的实验性的包。在下次稳定版本发布的时候，它们将成为独立的包。如果前一个版本已经存在了，它们将被作为过时的包被回收。然而 Go1.0 发布的时候并没有包含过时或者实验性的包。