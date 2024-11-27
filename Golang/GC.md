---
title: Golang GC
createTime: 2024-11-26
tags:
  - golang
author: ZQ
permalink: /golang/gc/
---
`go`的发行版优化和落地实践。

<!-- more -->
## 性能优化的层次

+ 业务代码
+ SDK
+ 基础库
+ `Go Runtime`
+ 操作系统

贴近业务的优化，更加针对场景，具体问题具体分析。容易获得较大的性能收益。
语言运行时优化，更加通用，能够赋能更多场景。

## 自动内存管理

+ Mutator : 业务线程，分配新的对象
+ Collector ：GC线程，找到存活对象，回收死亡对象

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Golang/GC%20Types.png)

**Concurrent GC的挑战**

GC时新的对象还在分配，所以必须在标记时考虑这种并发性。否则会遗漏标记新分配的存活对象。

## GC评价

+ Safety: 不能回收存活的对象
+ Throughput: 1 - (GC Time) / (Excution Time)
+ Pause Time: STW
+ Space Overhead: 元数据开销

## 追踪垃圾回收

+ 对象被回收的条件： 指针指向关系不可达的对象
+ 标记根对象
	+ 静态变量，全局变量， 常量，线程栈
+ 标记：找到可达对象
	+ 求指针指向关系传递闭包，从根对象出发，找到所有可达的对象
+ 清理：所有不可达对象
	+ 将存活对象复制到另外的空(Copying GC)
	+ 将死亡对象的空间标记为可分配(Mark-sweep GCV)
	+ 移动并且整理存活的对象(Mark-compact GC)
+ 根据对象的生命周期选择不同的标记和清理策略

### 分代假说

> most objects die young

+ 很多对象在分配出来之后很快就不使用了
+ 每个对象都有年龄: 经历GC的次数
+ 不同年龄的对象位于heap的不同区域

**年轻代**
+ 常规对象分配
+ 因为对象存活时间少，可以使用 copying collection gc
+ gc吞吐率高

**老年代**
+ 趋于一直存存活
+ 可以使用 mark-sweep collection

## 引用计数

+ 每个对象都有一个与之关联的引用数目
+ 对象存活的条件：当且仅当引用数目大于0

**优点**
+ 内存管理平摊到程序执行
+ 内存管理不需要了解 runtime 的实现细节 : C++ 智能指针

**缺点**
+ 维护引用计数的开销比较大
+ 无法回收环形数据结构
+ 每个对象都引入额外的内存空间存储引用数目
+ 回收仍然可能引发暂停

## Go内存分配

目标: 为对象在heap上分配内存

过程
+ 调用系统调用`mmap()` 向os申请一大块内存 比如 `4MB`
+ 将内存分为大块，比如 `8KB` 称为 `mspan`
	+ `noscan mspan`: 分配不包含指针的对象 - 不需要`GC`扫描
	+ `scan mspan`: 分配包含指针的对象 - 需要 `GC` 扫描
+ 继续将大块分为小块，用于对象分配
+ 根据对象大小，选择合适的块返回
