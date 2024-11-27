---
title: Golang Testing
createTime: 2024-11-21
tags:
  - golang
author: ZQ
permalink: /golang/testing/
---

`go`中常用的测试方法和工具。

<!-- more -->

## 单元测试

类似于判题机模式，在开发过程中编写测试用例，对某个模块，函数进行测试。

## 代码覆盖率

这个指标衡量测试用例是否完备。

```shell
➜  CodeCoverRate git:(main) tree           
.
├── cal.go
├── cal_test.go
├── coverage.html
├── coverage.out
├── go.mod
├── main.go
├── readme.md
└── test.sh

1 directory, 8 files
```

运行测试脚本，在命令行和浏览器中都可以查看测试结果。

```shell
# test.sh
#!/bin/bash

# 运行所有测试并生成覆盖率报告
echo "Running tests and generating coverage report..."
go test -coverprofile=coverage.out ./...

# 显示覆盖率统计信息
echo "Coverage summary:"
go tool cover -func=coverage.out

# 打开覆盖率的 HTML 报告
echo "Generating HTML coverage report..."
go tool cover -html=coverage.out -o coverage.html
echo "Done. Open 'coverage.html' in your browser to view the detailed coverage report."
```

```shell
➜  CodeCoverRate git:(main) ./test.sh 
Running tests and generating coverage report...
ok      zqzqsb.com/TestDemo     0.001s  coverage: 50.0% of statements
Coverage summary:
zqzqsb.com/TestDemo/cal.go:4:   Add             100.0%
zqzqsb.com/TestDemo/main.go:5:  main            0.0%
total:                          (statements)    50.0%
Generating HTML coverage report...
Done. Open 'coverage.html' in your browser to view the detailed coverage report.
```

## `pprof`性能分析

基于[go-pprof-practice](https://github.com/wolfogre/go-pprof-practice)

启动项目，程序运行在`6060`端口。

### 交互式分析

采样十秒

`go tool pprof "http://localhost:6060/debug/pprof/profile?seconds=10"`

使用`top`观测

```shell
➜  ~ go tool pprof "http://localhost:6060/debug/pprof/profile?seconds=10"
Fetching profile over HTTP from http://localhost:6060/debug/pprof/profile?seconds=10
Saved profile in /home/zq/pprof/pprof.main.samples.cpu.002.pb.gz
File: main
Type: cpu
Time: Nov 26, 2024 at 2:12pm (CST)
Duration: 10.15s, Total samples = 3.64s (35.85%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for 3.64s, 100% of 3.64s total
      flat  flat%   sum%        cum   cum%
     3.64s   100%   100%      3.64s   100%  github.com/wolfogre/go-pprof-practice/animal/felidae/tig
er.(*Tiger).Eat
         0     0%   100%      3.64s   100%  github.com/wolfogre/go-pprof-practice/animal/felidae/tig
er.(*Tiger).Live
         0     0%   100%      3.64s   100%  main.main
         0     0%   100%      3.64s   100%  runtime.main
(pprof)
```

使用`list`追踪到 `Tiger.Eat`

```shell
(pprof) list Eat
Total: 3.64s
ROUTINE ======================== github.com/wolfogre/go-pprof-practice/animal/felidae/tiger.(*Tiger)
.Eat in /home/zq/Projects/Learning/LearnGolang/ByteDance/Testing/PprofPractice/animal/felidae/tiger/
tiger.go
     3.64s      3.64s (flat, cum)   100% of Total
         .          .     19:}
         .          .     20:
         .          .     21:func (t *Tiger) Eat() {
         .          .     22:   log.Println(t.Name(), "eat")
         .          .     23:   loop := 10000000000
     3.64s      3.64s     24:   for i := 0; i < loop; i++ {
         .          .     25:           // do nothing
         .          .     26:   }
         .          .     27:}
         .          .     28:
         .          .     29:func (t *Tiger) Drink() {
(pprof)
```

### `web`可视化分析

使用`web`命令，可视化查看函数调用链调和各个环节的性能分析。

### `heap`占用

 `go tool pprof -http=:8080 "http://localhost:6060/debug/pprof/heap"`

在web端打开。

### `go-routine`

 `go tool pprof -http=:8080 "http://localhost:6060/debug/pprof/goroutine"`


### 其他

`block` 和 `metux`相关的方法的同上。

## `pprof` 采样过程和原理

### cpu

**原理**：

 + **信号驱动**：Go 运行时会定期向程序发送一个信号（通常是 SIGPROF），以触发采样。
 + **采样频率**：默认情况下，Go 的 CPU 采样频率为每秒 100 次（可以通过 GODEBUG 环境变量调整，如 GODEBUG=cpuprof=200）。
 + **采样内容**：每次采样时，运行时会捕获当前的 goroutine 的调用栈信息。
 
**流程**：
1. **定时信号**：运行时设置一个定时器，每隔一定时间发送一次 SIGPROF 信号
2. **信号处理**：收到信号后，Go 运行时会暂停当前 goroutine，捕获其调用栈信息。
3. **数据记录**：将捕获的调用栈信息记录到内存中的样本数据中。
4. **数据汇总**：在分析阶段，pprof 会根据采样数据汇总调用次数和时间消耗，生成性能报告。

### Heap Profiling

**原理**：

+ **追踪内存分配**：Go 运行时通过追踪内存分配事件来收集内存使用情况。
+ **采样频率**：内存分配并不像 CPU 使用那样定时，而是基于分配的次数和大小进行采样。
+ **采样内容**：记录内存分配的调用栈信息，包括分配位置和分配大小。

**流程**：

1. **内存分配追踪**：每当程序进行内存分配时，运行时会记录分配事件的调用栈信息。
2. **采样过滤**：为了减少开销，pprof 可能不会记录每一次内存分配，而是基于一定的采样率进行记录。
3. **数据记录**：将采样到的内存分配调用栈信息存储在样本数据中。
4. **数据汇总**：在分析阶段，pprof 会根据采样数据汇总内存分配次数和内存消耗，生成内存使用报告。

 ### Goroutine Profiling
 
**快照机制**

**快照** 是指在特定时间点收集所有 goroutine 的当前状态和调用栈信息。以下是快照采集的基本流程：

1. **触发快照**：

+ 通过发送特定的 HTTP 请求（如访问 /debug/pprof/goroutine），或使用 go tool pprof 命令来触发快照采集。
+ 例如，访问 `http://localhost:6060/debug/pprof/goroutine?debug=2` 会返回当前所有 `goroutine` 的详细信息。

2. **收集信息**：

+ Go 运行时会遍历所有活跃的 goroutine，记录每个 goroutine 的状态（如运行中、阻塞中、等待中等）和调用栈信息。这个过程会 `stop the world`

3. **生成报告**：

+ 收集到的信息被格式化为可读的报告，通常以文本形式展示每个 goroutine 的详细调用链。

### 性能优化对象

1. 接口的整个调用链路
2. 基础库
3. `go`语言本身






