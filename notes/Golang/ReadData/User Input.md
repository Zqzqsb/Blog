---
title: Read data from user input.
createTime: 2024-11-8
tags:
  - Golang
permalink: /note/golang/readdata/userinput/
---

## 概述

本章节讲述`go`从各种数据源读取数据的方式。

## 读取用户输入

### 使用`fmt`

```go
package main
import "fmt"

var (
   firstName, lastName, s string
   i int
   f float32
   input = "56.12 / 5212 / Go"
   format = "%f / %d / %s"
)

func main() {
   fmt.Println("Please enter your full name: ")
   // 以空格分割读取输入,直到遇到换行为止 (类C语法)
   fmt.Scanln(&firstName, &lastName)
   // 同下 
   // fmt.Scanf("%s %s", &firstName, &lastName)
   
   //  类C语法的Printf函数
   fmt.Printf("Hi %s %s!\n", firstName, lastName) // Hi Chris Naegels
   // 期待输入(解析占位符之后的format)和input对齐
   fmt.Sscanf(input, format, &f, &i, &s)
   
   fmt.Println("From the string we read: ", f, i, s)
   // 输出结果: From the string we read: 56.12 5212 Go
}
```

### 使用 `bufio`

```go
package main
import (
    "fmt"
    "bufio"
    "os"
)

var inputReader *bufio.Reader
var input string
var err error

func main() {
    inputReader = bufio.NewReader(os.Stdin)
    fmt.Println("Please enter some input: ")
    // 使用bufio的Reader读入一行
    input, err = inputReader.ReadString('\n')
    if err == nil {
        fmt.Printf("The input was: %s\n", input)
    }
}
```

+ `bufio.NewReader()` 构造函数的签名为：`func NewReader(rd io.Reader) *Reader`，返回的读取器对象提供一个方法 `ReadString(delim byte)`，该方法从输入中读取内容，直到碰到 `delim` 指定的字符，然后将读取到的内容连同 `delim` 字符一起放到缓冲区。
+ `ReadString` 返回读取到的字符串，如果碰到错误则返回 `nil`。如果它一直读到文件结束，则返回读取到的字符串和 `io.EOF`。如果读取过程中没有碰到 `delim` 字符，将返回错误 `err != nil`。
+ 在上面的例子中，我们会读取键盘输入，直到回车键（\n）被按下。

## 命令行参数

os 包中有一个 string 类型的切片变量 `os.Args`，用来处理一些基本的命令行参数，它在程序启动后读取命令行输入的参数。

```go
// os_args.go
package main

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	who := "Alice "
	if len(os.Args) > 1 {
		who += strings.Join(os.Args[1:], " ")
	}
	fmt.Println("Good Morning", who)
}
```

### `flag`包

flag 包有一个扩展功能用来解析命令行选项。但是通常被用来替换基本常量，例如，在某些情况下我们希望在命令行给常量一些不一样的值。

#### 1. **定义命令行参数**

`flag` 提供了多种函数用于定义不同类型的命令行参数：

- `flag.Bool(name string, default bool, usage string)`：定义布尔类型的 flag，命令行中若出现该选项，其值设为 `true`。
- `flag.Int(name string, default int, usage string)`：定义整数类型的 flag。
- `flag.Float64(name string, default float64, usage string)`：定义浮点数类型的 flag。
- `flag.String(name string, default string, usage string)`：定义字符串类型的 flag。

#### 2. **解析命令行参数**

调用 `flag.Parse()` 解析命令行输入，将用户提供的值赋予定义的 flag。如果没有提供值，则使用默认值。

#### 3. **获取解析后的值**

`flag` 定义的每个 flag 会返回一个指向对应类型的指针（例如，`*bool`、`*int`、`*string`）。通过解引用可以获取该 flag 的值。

#### 4. **其他辅助方法**

- `flag.NArg()`：返回命令行中非 flag 参数（位置参数）的个数。
- `flag.Arg(i)`：获取第 `i` 个非 flag 参数。
- `flag.PrintDefaults()`：打印所有 flag 的帮助信息，包括名称、默认值和用途。
- `flag.VisitAll(fn func(*Flag))`：遍历所有 flag。

```go
package main

import (
	"flag" // command line option parser
	"os"
)

// 全局变量 NewLine Flag
var NewLine = flag.Bool("n", false, "print newline") // echo -n flag, of type *bool

// 常量
const (
	Space   = " "
	Newline = "\n"
)

func main() {
	flag.PrintDefaults()
	flag.Parse() // Scans the arg list and sets up flags
	var s string = ""
	for i := 0; i < flag.NArg(); i++ {
		if i > 0 {
			s += " "
			if *NewLine { // -n is parsed, flag becomes true
				s += Newline
			}
		}
		s += flag.Arg(i)
	}
	os.Stdout.WriteString(s)
}
```

### 使用 `bufio`实现简单`cat`

```go
package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
)

func cat(r *bufio.Reader) {
	for {
		buf, err := r.ReadBytes('\n')
		fmt.Fprintf(os.Stdout, "%s", buf)
		if err == io.EOF {
			break
		}
	}
	return
}

func main() {
	flag.Parse()
	if flag.NArg() == 0 {
		cat(bufio.NewReader(os.Stdin))
	}
	for i := 0; i < flag.NArg(); i++ {
		f, err := os.Open(flag.Arg(i))
		if err != nil {
			fmt.Fprintf(os.Stderr, "%s:error reading from %s: %s\n", os.Args[0], flag.Arg(i), err.Error())
			continue
		}
		cat(bufio.NewReader(f))
		f.Close()
	}
}
```