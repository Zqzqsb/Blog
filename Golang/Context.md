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