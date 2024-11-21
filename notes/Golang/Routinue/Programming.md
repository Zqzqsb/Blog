---
title: Go Routine intro.
createTime: 2024-11-20
tags:
  - Golang
description: 笔记记录了Goroutine的编程实践
permalink: /note/golang/routinue/programming/
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

### 通道的方向

通道类型可以用注解来表示它只发送或者只接收：

```go
var send_only chan<- int 		// channel can only receive data
var recv_only <-chan int		// channel can only send data
```

只接收的通道（<-chan T）无法关闭，因为关闭通道是发送者用来表示不再给通道发送值了，所以对只接收通道是没有意义的。

```go
func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i // 只能发送
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for v := range ch { // 只能接收
        fmt.Println(v)
    }
}

func main() {
    ch := make(chan int)
    go producer(ch)
    consumer(ch)
}
```

使用单向通道明确了两者的职责。
## 质数筛

```go
package main

import "fmt"

// Send the sequence 2, 3, 4, ... to channel 'ch'.
func generate(ch chan int) {
	for i := 2; ; i++ {
		ch <- i // Send 'i' to channel 'ch'.
	}
}

func filter(in, out chan int, prime int) {
	for {
		i := <-in
		if i%prime != 0 { // 筛掉能被 prime 整除的数
			out <- i
		}
	}
}

// The prime sieve: Daisy-chain filter processes together.
func main() {
	ch := make(chan int) // 初始通道
	go generate(ch)      // 启动生成器
	for {
		prime := <-ch    // 从通道中获取第一个素数(获得的第一个数必定是素数)
		fmt.Print(prime, " ") // 打印素数
		ch1 := make(chan int) // 为下一轮筛选创建一个新的通道
		go filter(ch, ch1, prime) // 启动筛选器协程
		ch = ch1            // 将 ch 设置为新的通道，用于下一轮筛选
	}
}
```

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Notes/golang/PrimeSieve.png)
## 信号量模式

**信号量模式的基本思想**

信号量模式通过 **channel** 实现协程（goroutine）之间的同步：

+ 一个协程完成任务后，通过向 channel 发送信号（即发送值）来通知主协程。
+ 主协程通过从 channel 接收信号来等待协程完成。

这种模式非常适合以下场景：

+ 主协程需要等待某些任务完成。
+ 需要并发运行多个任务，并在所有任务完成后继续执行主协程的逻辑。

### 资源控制

```go
package main

// 50个信号量
const MAXREQS = 50

var sem = make(chan int, MAXREQS)

type Request struct {
	a, b   int
	replyc chan int
}

func process(r *Request) {
	// do something
}

func handle(r *Request) {
	sem <- 1 // doesn't matter what we put in it
	process(r) // 临界区
	<-sem // one empty place in the buffer: the next request can start
}

func server(service chan *Request) {
	for {
		request := <-service
		go handle(request)
	}
}

func main() {
	service := make(chan *Request)
	go server(service)
}
```

## 测试

检测通道是否关闭或者阻塞。

```go
ch := make(chan float64)
defer close(ch)
```

## 关闭通道

使用 `close(ch)`  显式关闭。

检测通道状态

```go
v, ok := <-ch
```

`for-range` 会自动检测通道是否关闭

```go
for v := range ch {
    process(v)
}
```

## 切换协程

从不同的并发执行的协程中获取值可以通过关键字`select`来完成，它的行为像是“你准备好了吗”的轮询机制。

```go
select {
case u:= <- ch1:
        ...
case v:= <- ch2:
        ...
        ...
default: // no value ready to be received
        ...
}
```

`default` 语句是可选的；

`select` 做的就是：选择处理列出的多个通信情况中的一个。

- 如果都阻塞了，会等待直到其中一个可以处理
- 如果多个可以处理，随机选择一个
- 如果没有通道操作可以处理并且写了 `default` 语句，它就会执行：`default` 永远是可运行的（这就是准备好了，可以执行）。

在 `select` 中使用发送操作并且有 `default` 可以确保发送不被阻塞！如果没有 `default`，select 就会一直阻塞。

`select` 语句实现了一种监听模式，通常用在（无限）循环中；在某种情况下，通过 `break` 语句使循环退出。

## 定时器

### 周期性任务

time.Ticker 是 Go 中提供的一个工具，用于以固定的时间间隔向通道发送当前时间。它适用于定时任务，例如周期性日志、状态更新或限速。

```go
ticker := time.NewTicker(1 * time.Second) // 每秒触发一次
defer ticker.Stop()                      // 程序结束前停止 Ticker

for {
    select {
    case <-ticker.C:
        fmt.Println("Tick...")
    }
}
```

### 无关闭通道

time.Tick 是一个简单的工厂函数，返回一个定时触发的通道，但它的通道无法关闭。

+ time.NewTicker 返回一个 Ticker 对象，支持通过 Stop() 方法停止。
+ time.Tick 只返回通道，无法显式停止。

```go
ch := time.Tick(1 * time.Second) // 每秒触发一次
for now := range ch {
    fmt.Println("Time:", now)
}
```

### 触发超时

time.Timer 是另一个定时工具，用于在指定时间后触发一次。

```go
timer := time.NewTimer(5 * time.Second) // 5 秒后触发
<-timer.C                              // 等待触发
fmt.Println("Timer expired")

// 下同
<-time.After(5 * time.Second)
fmt.Println("Time expired")
```

### 超时控制

```go
ch := make(chan int)
go func() {
    time.Sleep(2 * time.Second) // 模拟延迟
    ch <- 42
}()

select {
case data := <-ch:
    fmt.Println("Received:", data)
case <-time.After(1 * time.Second): // 每次轮训都会阻塞一秒
    fmt.Println("Timeout")
}
```

### 限速控制

**需求:** 每秒最多处理10个请求。

```go
rate := time.Tick(100 * time.Millisecond) // 每 100ms 限制一次请求
requests := make(chan int, 100)

go func() {
    for i := 0; i < 100; i++ {
        requests <- i
    }
    close(requests)
}()

for req := range requests {
    <-rate // 等待下一个时间点
    fmt.Println("Processing request", req)
}
```

## 协程恢复

```go
func server(workChan <-chan *Work) {
    for work := range workChan {
        go safelyDo(work)   // start the goroutine for that work
    }
}

func safelyDo(work *Work) {
    defer func() {
	    // 捕获 panic
        if err := recover(); err != nil {
            log.Printf("Work failed with %s in %v", err, work)
        }
    }()
    do(work)
}
```

## 惰性生成器

以生成自然数为例。

```go
package main

import "fmt"

// 自然数生成器
func naturalNumbers() <-chan int {
    ch := make(chan int) // 创建一个通道
    go func() {
        for i := 1; ; i++ {
            ch <- i // 按需发送自然数
        }
    }()
    return ch
}

func main() {
    gen := naturalNumbers() // 获取生成器

    for i := 0; i < 10; i++ {
        fmt.Println(<-gen) // 每次从生成器中获取一个值
    }
}
```

## `Future`模式

  **核心思想：** 将一个值的计算分离到异步任务中，主流程在需要这个值时，通过一个「占位符」（Future）来获取。

**实现方式：** 使用 Goroutine 和 Channel，通过 Channel 异步接收计算结果。

### 串行计算

```go
func InverseProduct(a Matrix, b Matrix) Matrix {
    a_inv := Inverse(a) // 串行求逆
    b_inv := Inverse(b)
    return Product(a_inv, b_inv)
}
```

### 并行实现

```go
func InverseProduct(a Matrix, b Matrix) Matrix {
    // 使用 Futures 并行计算
    a_inv_future := InverseFuture(a)  // 异步计算 a 的逆
    b_inv_future := InverseFuture(b)  // 异步计算 b 的逆

    // 获取结果，阻塞直到计算完成
    a_inv := <-a_inv_future
    b_inv := <-b_inv_future

    return Product(a_inv, b_inv)
}

```

## 链式协程

```go
package main

import (
	"flag"
	"fmt"
)

var ngoroutine = flag.Int("n", 100000, "how many goroutines")

func f(left, right chan int) { left <- 1 + <-right }

func main() {
	flag.Parse()
	leftmost := make(chan int)
	var left, right chan int = nil, leftmost
	for i := 0; i < *ngoroutine; i++ {
		left, right = right, make(chan int) // 左等于右 右等于新 
		go f(left, right) // 像构造链表一样串起诺干个通道
	}
	right <- 0      // 从右侧开始传递
	x := <-leftmost 
	fmt.Println(x)  
}
```
