---
title: Error in golang.
createTime: 2024-11-20
tags:
  - Golang
description: 笔记记录了go中的错误机制。
permalink: /note/golang/error/
---

## 概述

Go 没有像 `try/catch` 异常机制：不能执行抛异常操作。但是有一套 `defer-panic-and-recover` 

Go 的设计者觉得 `try/catch` 机制的使用太泛滥了，而且从底层向更高的层级抛异常太耗费资源。他们给 Go 设计的机制也可以 “捕捉” 异常，但是更轻量，并且只应该作为（处理错误的）最后的手段。

## 使用双返回

使用双返回处理错误是`go`编程实践中的常用范式。

```go
if value, err := pack1.Func1(param1); err != nil {
	fmt.Printf("Error %s in pack1.Func1 with parameter %v", err.Error(), param1)
	return    // or: return err
} else {
	// Process(value)
}
```

## 错误结构

`go`中有一个预定义的错误的接口。
«
```go
type error interface {
	Error() string
}
```

任何时候当你需要一个新的错误类型，都可以用 errors（必须先 import）包的 errors.New 函数接收合适的错误信息来创建，像下面这样

```go
err := errors.New("math - square root of negative number")

func Sqrt(f float64) (float64, error) {
	if f < 0 {
		return 0, errors.New ("math - square root of negative number")
	}
   // implementation of Sqrt
}
```

### 自定义错误结构

```go
// PathError records an error and the operation and file path that caused it.
type PathError struct {
	Op string    // "open", "unlink", etc.
	Path string  // The associated file.
	Err error  // Returned by the system call.
}

// 实现了重载
func (e *PathError) Error() string {
	return e.Op + " " + e.Path + ": "+ e.Err.Error()
}
```

## `Panic`

当发生像数组下标越界或类型断言失败这样的运行错误时，Go 运行时会触发运行时`panic`，伴随着程序的崩溃抛出一个 `runtime.Error` 接口类型的值。这个错误值有个 `RuntimeError()` 方法用于区别普通错误。

```go
package main

import "fmt"

func main() {
	fmt.Println("Starting the program")
	panic("A severe error occurred: stopping the program!")
	fmt.Println("Ending the program")
}
```

环境变量检查

```go
var user = os.Getenv("USER")

func check() {
	if user == "" {
		panic("Unknown user: no value for $USER")
	}
}
```

在多层嵌套的函数调用中调用 panic，可以马上中止当前函数的执行，所有的 defer 语句都会保证执行并把控制权交还给接收到 panic 的函数调用者。这样向上冒泡直到最顶层，并执行（每层的） defer，在栈顶处程序崩溃，并在命令行中用传给 panic 的值报告错误情况：这个终止过程就是 _panicking_。

标准库中有许多包含 `Must` 前缀的函数，像 `regexp.MustComplie` 和 `template.Must`；当正则表达式或模板中转入的转换字符串导致错误时，这些函数会 panic。

不能随意地用 panic 中止程序，必须尽力补救错误让程序能继续执行。

### 恢复


正如名字一样，内建函数`recover`被用于从 panic 或 错误场景中恢复：让程序可以从 panicking 重新获得控制权，停止终止过程进而恢复正常执行。

`recover` 只能在 `defer` 修饰的函数中使用：用于取得`panic` 调用中传递过来的错误值，如果是正常执行，调用 `recover` 会返回 `nil`，且没有其它效果。

```go
func protect(g func()) {
	defer func() {
		log.Println("done")
		// Println executes normally even if there is a panic
		if err := recover(); err != nil {
			log.Printf("run time panic: %v", err)
		}
	}()
	log.Println("start")
	g() //   possible runtime-error
	// 往下不会执行
}
```


+ `defer` 中调用了 `recover()`，如果捕获到异常（panic），会将其存储在 e 中，并打印相关信息。
+ `g()` 调用会触发 panic，此时控制权交给了 defer 中的匿名函数。
+ 因为 panic 被捕获并处理，程序不会崩溃，但 badCall 之后的代码不会继续执行。

### 自定义包

在自定义包中编程应该遵循的最佳实践:

+ 在包内部，总是应该从 panic 中 recover，不允许显式的超出包范围的 panic()
+ 向包的调用者返回错误值。

### 使用闭包处理错误

原函数的签名

```go
fType1 = func f(a type1, b type2)
```

在原函数中`panic`
```go
func check(err error) { if err != nil { panic(err) } }

func f1(a type1, b type2) {
	...
	f, _, err := // call function/method
	check(err)
	t, err := // call function/method
	check(err)
	_, err2 := // call function/method
	check(err2)
	...
}
```

原函数的错误包装器

```go
func errorHandler(fn fType1) fType1 {
	return func(a type1, b type2) {
		defer func() {
			if err, ok := recover().(error); ok {
				log.Printf("run time panic: %v", err)
			}
		}()
		fn(a, b)
	}
}
```

## 启动外部程序

```go
// exec.go
package main
import (
	"fmt"
    "os/exec"
	"os"
)

func main() {
// 1) os.StartProcess //
/*********************/
/* Linux: */
env := os.Environ() // 系统当前的环境变量
procAttr := &os.ProcAttr{
			Env: env, 
			Files: []*os.File{
				os.Stdin,
				os.Stdout,
				os.Stderr,
			},
		}
// 1st example: list files
pid, err := os.StartProcess("/bin/ls", []string{"ls", "-l"}, procAttr) 

if err != nil {
		fmt.Printf("Error %v starting process!", err)  //
		os.Exit(1)
}
fmt.Printf("The process id is %v", pid)
```

`func StartProcess(name string, argv []string, attr *os.ProcAttr) (*os.Process, error)`

+ name：要启动的可执行程序的路径。
+ argv：程序的参数列表，第一个参数通常是程序本身的名称。
+ attr：进程属性，*os.ProcAttr 类型，用于指定子进程的环境、文件描述符等。
+ 返回值：
	+ os.Process：表示子进程的句柄
	+ errror：如果出错则返回错误。







