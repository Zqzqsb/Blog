---
title: Go Routine and channel
createTime: 2024-11-6
tags:
  - Golang
description: 笔记记录了Golang中的Map相关。
permalink: /note/golang/routinue/
---
 笔记记录了Golang中的Map相关。
<!-- more -->

## 概述

Go 原生支持应用之间的通信和程序的并发。程序可以在不同的处理器和计算机上同时执行不同的代码段。Go 语言为构建并发程序的基本代码块是 协程 (goroutine) 与通道 (channel)。他们需要语言，编译器，和runtime的支持。Go 语言提供的垃圾回收器对并发编程至关重要。
