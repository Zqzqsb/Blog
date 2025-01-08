---
title: Golang Context
createTime: 2024-12-25
tags:
  - golang
author: ZQ
permalink: /golang/context/
---

`context` 提供了在 Go 程序中跨 API 边界和 goroutine 传递取消信号、截止时间和请求范围值的机制。它在构建高并发、可取消和可管理的应用程序时尤为重要。

本文将详细介绍 `context` 包的关键概念、常用模式、最佳实践以及相关的衍生知识。我们还将通过几个示例程序来展示如何在实际项目中有效地使用 `context`。

<!-- more -->

## 概述

`context` 包在 Go 1.7 中引入，用于在不同的 goroutine 之间传递取消信号、截止时间和请求范围的值。它主要解决了以下问题：

- **取消信号传递**：在多个 goroutine 中协同工作时，能够通知所有相关 goroutine 取消操作。
- **截止时间和超时控制**：为一组操作设置统一的截止时间或超时。
- **请求范围值传递**：在 API 边界之间传递特定于请求的值，如认证信息、追踪 ID 等。

`context` 提供了一种统一的方式来管理这些需求，从而增强了程序的可维护性和可扩展性

## 常用类型和函数

`context` 包主要提供以下类型和函数：

### 主要类型

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)
    Done() <-chan struct{}
    Err() error
    Value(key interface{}) interface{}
}
```

- **Deadline()**：返回上下文的截止时间和是否设置了截止时间。
- **Done()**：返回一个在上下文被取消或截止时间到达时关闭的通道。
- **Err()**：返回上下文被取消的原因，可能的值为 `context.Canceled` 或 `context.DeadlineExceeded`。
- **Value(key interface{})**：用于在上下文中存储和检索值。

### 主要函数

以下内容摘自`context`源码。

#### `Background`

```go
func Background() Context {
	return backgroundCtx{}
}
```

• **用途**：创建一个空的根上下文，通常作为所有其他上下文的起点。
• **特点**：
	• 不可取消。
	• 没有截止时间。
	• 不携带任何值。
• **使用场景**：应用程序的主函数、初始化代码或测试环境中作为顶层上下文。

#### `TODO`

```go
func TODO() Context {
	return todoCtx{}
}
```

• **用途**：创建一个空的上下文，用于尚未确定具体上下文用途的场景。
• **特点**：
	• 不可取消。
	• 没有截止时间。
	• 不携带任何值。
• **使用场景**：开发过程中暂时需要上下文但不确定具体需求时的占位符。

#### `WithCancel`

```go

type CancelFunc func()

func WithCancel(parent Context) (ctx Context, cancel CancelFunc) {
	c := withCancel(parent)
	return c, func() { c.cancel(true, Canceled, nil) }
}
```

• **用途**：基于父上下文创建一个带有具体截止时间的子上下文。
• **返回值**：
	• **Context**：新的子上下文。
	• **CancelFunc**：用于取消子上下文的函数。
• **特点**：
	• 子上下文会在指定的截止时间自动取消。
	• 可以通过手动调用 CancelFunc 提前取消。
• **使用场景**：需要为操作设置具体的截止时间，以确保操作不会无限期阻塞。

### 更多

还有`WithTimeout()` , `WithDeadline()` , `WithValue`等等，`context`包源码中有实现和详细说明。

## 编程例子

### 基本使用

```go
package context

import (
        "context"
        "fmt"
        "testing"
        "time"
)

func TestContext(t *testing.T) {
        // context.Background() 是创建根上下文（root context）的函数，通常用于应用程序的顶层上下文。
        // 它返回一个空的、不可取消的上下文，且没有截止时间或值。这使得它成为所有其他上下文派生的基础 。
        // ctx 是新创建的上下文， cancel是其取消函数
        ctx, cancel := context.WithCancel(context.Background())
        defer cancel()

        go func() {
                time.Sleep(2 * time.Second) // 等待2秒
                cancel()                    // 取消上下文
        }()

        // select {
        // case <-ctx.Done(): // 等待上下文被取消
        //      fmt.Println("Context Canceled!", ctx.Err()) // 输出上下文被取消的信息
        // }
        <-ctx.Done()                                // 等待上下文被取消
        fmt.Println("Context Canceled!", ctx.Err()) // 输出上下文被取消的信息
}
```

### 限制程序的运行时间

```go
package context

import (
        "context"
        "fmt"
        "testing"
        "time"
)

func TestUsageTimeout(t *testing.T) {
        // 1s context timeout
        ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
        defer cancel()

        // launch a long running operation needing 2s
        err := longRunningOperation(ctx, 2*time.Second)

        if err != nil {
                fmt.Println("Operation failed:", err)
        } else {
                fmt.Println("Operation succeeded!")
        }
}

func longRunningOperation(ctx context.Context, duration time.Duration) error {
        for {
                select {
                case <-ctx.Done():
                        return ctx.Err() // context timetout
                case <-time.After(duration):
                        return nil // operation succeeded
                default:
                        println("Operation is still running!")
                        time.Sleep(500 * time.Millisecond)
                }
        }
}
```

### 取消执行协程

```go
package context

import (
        "context"
        "fmt"
        "testing"
        "time"
)

func TestCancelUsage(t *testing.T) {
        ctx, cancel := context.WithCancel(context.Background())

        go func() {
                for {
                        select {
                        case <-ctx.Done():
                                fmt.Println("Goroutine received cancel signal!")
                                return
                        default:
                                fmt.Println("Goroutine is still running!")
                                time.Sleep(500 * time.Millisecond)
                        }
                }
        }()

        time.Sleep(2 * time.Second)
        cancel()

        time.Sleep(1 * time.Second)
}
```

### 在协程之间传递值

```go
package context

import (
        "context"
        "testing"
)

type key string

func TestPassValue(t *testing.T) {
        ctx := context.WithValue(context.Background(), key("userID"), 123)
        printUserID(ctx)
}

func printUserID(ctx context.Context) {
        if val, ok := ctx.Value(key("userID")).(int); ok {
                println("userID is", val)
        } else {
                println("userID not found")
        }
}
```