---
title: Go Routine intro.
createTime: 2024-11-20
tags:
  - Golang
description: 笔记记录了Goroutine的编程实践
permalink: /note/golang/routinue/intro/
---
 笔记记录了Goroutine的编程实践
<!-- more -->
## 例子1 

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("In main()")
	go longWait()
	go shortWait()
	fmt.Println("About to sleep in main()")
	// sleep works with a Duration in nanoseconds (ns) !
	time.Sleep(10 * 1e9)
	fmt.Println("At the end of main()")
}

func longWait() {
	fmt.Println("Beginning longWait()")
	time.Sleep(5 * 1e9) // sleep for 5 seconds
	fmt.Println("End of longWait()")
}

func shortWait() {
	fmt.Println("Beginning shortWait()")
	time.Sleep(2 * 1e9) // sleep for 2 seconds
	fmt.Println("End of shortWait()")
}
```

开启了两个协程并且独立执行。

```
In main()
About to sleep in main()
Beginning longWait()
Beginning shortWait()
End of shortWait()
End of longWait()
At the end of main() // after 10s
```

## 使用 GOMAXPROCS

在 gc 编译器下（6g 或者 8g）你必须设置 GOMAXPROCS 为一个大于默认值 1 的数值来允许运行时支持使用多于 1 个的操作系统线程，所有的协程都会共享同一个线程除非将 GOMAXPROCS 设置为一个大于 1 的数。当 GOMAXPROCS 大于 1 时，会有一个线程池管理许多的线程。通过 `gccgo` 编译器 GOMAXPROCS 有效的与运行中的协程数量相等。假设 n 是机器上处理器或者核心的数量。如果你设置环境变量 GOMAXPROCS>=n，或者执行 `runtime.GOMAXPROCS(n)`，接下来协程会被分割（分散）到 n 个处理器上。更多的处理器并不意味着性能的线性提升。有这样一个经验法则，对于 n 个核心的情况设置 GOMAXPROCS 为 n-1 以获得最佳性能，也同样需要遵守这条规则：协程的数量 > 1 + GOMAXPROCS > 1。

所以如果在某一时间只有一个协程在执行，不要设置 GOMAXPROCS！

还有一些通过实验观察到的现象：在一台 1 颗 CPU 的笔记本电脑上，增加 GOMAXPROCS 到 9 会带来性能提升。在一台 32 核的机器上，设置 GOMAXPROCS=8 会达到最好的性能，在测试环境中，更高的数值无法提升性能。如果设置一个很大的 GOMAXPROCS 只会带来轻微的性能下降；设置 GOMAXPROCS=100，使用 `top` 命令和 `H` 选项查看到只有 7 个活动的线程。

增加 GOMAXPROCS 的数值对程序进行并发计算是有好处的；

总结：GOMAXPROCS 等同于（并发的）线程数量，在一台核心数多于1个的机器上，会尽可能有等同于核心数的线程在并行运行.

## Channel

通道（channel），就像一个可以用于发送类型化数据的管道，由其负责协程之间的通信，从而避开所有由共享内存导致的陷阱；这种通过通道进行通信的方式保证了同步性。数据在通道中进行传递：_在任何给定时间，一个数据被设计为只有一个协程可以对其访问，所以不会发生数据竞争。_ 数据的所有权（可以读写数据的能力）也因此被传递。

```go
package main

import (
	"fmt"
)

// worker 函数，用于计算数组一部分的和，并将结果发送到通道
func worker(nums []int, ch chan int) {
	sum := 0
	for _, num := range nums {
		sum += num
	}
	// 将计算结果发送到 channel
	ch <- sum
}

func main() {
	// 定义一个大数组
	nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

	// 创建一个 channel，用于传递部分和
	ch := make(chan int)

	// 启动两个 Goroutines，分别计算数组的前半部分和后半部分的和
	go worker(nums[:len(nums)/2], ch) // 前半部分
	go worker(nums[len(nums)/2:], ch) // 后半部分

	// 从 channel 接收两个部分的结果
	sum1 := <-ch
	sum2 := <-ch

	// 计算总和
	total := sum1 + sum2

	// 打印结果
	fmt.Println("总和:", total)
}
```

### 创建

```go
ch := make(chan int)
```

+ make(chan int) 创建了一个无缓冲的整型通道。
+ 无缓冲的 Channel 是同步的(阻塞的)，发送和接收操作必须同时进行，才能完成传递。

**带缓冲的 Channel**

如果容量大于 0，通道就是异步的了：缓冲满载（发送）或变空（接收）之前通信不会阻塞，元素会按照发送的顺序被接收。如果容量是0或者未设置，通信仅在收发双方准备好的情况下才可以成功。

```go
ch := make(chan int, 2) // 创建一个容量为 2 的缓冲 Channel
```

**关闭 Channel**

```go
close(ch)
```

关闭 Channel 后，可以使用 range 遍历 Channel 的数据。

```go
go func() {
    for i := 1; i <= 5; i++ {
        ch <- i
    }
    close(ch)
}()

for v := range ch {
    fmt.Println(v) // 依次输出 1, 2, 3, 4, 5
}
```

## 信号量模式

**信号量模式的基本思想**

信号量模式通过 **channel** 实现协程（goroutine）之间的同步：

+ 一个协程完成任务后，通过向 channel 发送信号（即发送值）来通知主协程。
+ 主协程通过从 channel 接收信号来等待协程完成。

这种模式非常适合以下场景：

+ 主协程需要等待某些任务完成。
+ 需要并发运行多个任务，并在所有任务完成后继续执行主协程的逻辑。
