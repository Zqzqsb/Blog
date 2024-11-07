---
title: Golang Startup
createTime: 2024-11-6
tags:
  - golang
author: ZQ
permalink: /golang/startup/
---

最近参加了字节的青训营，有机会可以任务驱动式的系统学习一下`golang`。该系列笔记会同步发布掘金。

<!-- more -->
## 介绍

**golang的特点**

| 特点         | 描述                   |
| ---------- | -------------------- |
| 高性能，高并发    | 接近C++的性能，标准库原生高并发支持。 |
| 语法简单，学习曲线缓 | 学习周期短至周计             |
| 丰富的标准库     | 可以解决大部分需求            |
| 工具链        | 编译，代码格式化，代码检查，测试     |
| 静态编译       | 体积小，部署编译             |
| 快速编译       | 支持增量编译               |
| 快平台        | 交叉编译简单               |
| GC         | 原生GC支持               |
## 开发环境

这里我使用的是 `gvm` 在`debian12`上进行开发。开发环境使用`vscode` + `neovim`。

`gvm` 的 [github链接](https://github.com/moovweb/gvm)

我练习的源码已经托管在[github](https://github.com/Zqzqsb/LearnGolang)

## 基本语法

由于之前已经学过一些基本语法。这部分可以直接转到[博客](https://blog.zqzqsb.cn/notes/Golang/)的笔记。

## 练手程序

### [猜数字](https://github.com/Zqzqsb/LearnGolang/blob/main/ByteDance/Lesson1/GussingGame.go)

```go
package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

func main() {
	maxNum := 1000
	rand.Seed(time.Now().UnixNano())
	secretNumber := rand.Intn(maxNum)
	// fmt.Println("The secret number is", secretNumber)

	fmt.Println("Please input your guess")
	reader := bufio.NewReader(os.Stdin) // 将系统输入转换为 bufio

	for {
		input, err := reader.ReadString('\n')

		if err != nil {
			fmt.Println("error ouccered , try again!")
			continue
		}

		input = strings.Trim(input, "\r\n")

		guess, err := strconv.Atoi(input)

		if err != nil {
			fmt.Println("Invalid Number. Please input a number!")
			continue
		}

		fmt.Println("You guess is", guess)

		if guess > secretNumber {
			fmt.Println("Guess too big!")
		} else if guess < secretNumber {
			fmt.Println("Guess too small!")
		} else {
			fmt.Print("You are right!")
			break
		}
	}
}
```