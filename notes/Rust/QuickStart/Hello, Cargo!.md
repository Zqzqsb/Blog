---
title: Create Project with Cargo.
createTime: 2024-7-28
tags:
  - Rust
description: 怎样从cargo创建项目。
---
<br> 怎样从cargo创建项目。
<!-- more -->

## Cargo

Cargo 是 Rust 的构建系统和包管理器。大多数 Rustacean 们使用 Cargo 来管理他们的 Rust 项目，因为它可以为你处理很多任务，比如构建代码、下载依赖库并编译这些库。（我们把代码所需要的库叫做 **依赖**（_dependencies_））。

最简单的 Rust 程序，比如我们刚刚编写的，没有任何依赖。如果使用 Cargo 来构建 “Hello, world!” 项目，将只会用到 Cargo 构建代码的那部分功能。在编写更复杂的 Rust 程序时，你将添加依赖项，如果使用 Cargo 启动项目，则添加依赖项将更容易。

由于绝大多数 Rust 项目使用 Cargo，本书接下来的部分假设你也使用 Cargo。如果使用 [“安装”](https://kaisery.github.io/trpl-zh-cn/ch01-01-installation.html#%E5%AE%89%E8%A3%85) 部分介绍的官方安装包的话，则自带了 Cargo。如果通过其他方式安装的话，可以在终端输入如下命令检查是否安装了 Cargo：

## 使用 `cargo` 创建一个项目

```shell
➜  QuickStart ls
HelloWorld
➜  QuickStart cargo --version
cargo 1.80.0 (376290515 2024-07-16)
```

```shell
cargo new HelloCargo --vcs none
```

```shell
➜  HelloCargo git:(master) ✗ tree           
.
├── Cargo.toml
└── src
    └── main.rs

2 directories, 2 files
```

进入 _hello_cargo_ 目录并列出文件。将会看到 Cargo 生成了两个文件和一个目录：一个 _Cargo.toml_ 文件，一个 _src_ 目录，以及位于 _src_ 目录中的 _main.rs_ 文件。

这也会在 _hello_cargo_ 目录初始化了一个 git 仓库，以及一个 _.gitignore_ 文件。如果在一个已经存在的 git 仓库中运行 `cargo new`，则这些 git 相关文件则不会生成；可以通过运行 `cargo new --vcs=git` 来覆盖这些行为。

## `Cargo.toml`

```
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]

```


这个文件使用 [_TOML_](https://toml.io/) (_Tom's Obvious, Minimal Language_) 格式，这是 Cargo 配置文件的格式。

第一行，`[package]`，是一个片段（section）标题，表明下面的语句用来配置一个包。随着我们在这个文件增加更多的信息，还将增加其他片段（section）。

接下来的三行设置了 Cargo 编译程序所需的配置：项目的名称、项目的版本以及要使用的 Rust 版本。[附录 E](https://kaisery.github.io/trpl-zh-cn/appendix-05-editions.html) 会介绍 `edition` 的值。

最后一行，`[dependencies]`，是罗列项目依赖的片段的开始。在 Rust 中，代码包被称为 _crates_。这个项目并不需要其他的 crate，不过在第二章的第一个项目会用到依赖，那时会用得上这个片段。

## 构建和运行`Cargo` 项目

```shell
➜  HelloCargo cargo build                     
   Compiling HelloCargo v0.1.0 (/home/zq/Projects/Learning/LearnRust/QuickStart/HelloCargo)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.11s
```

```shell
➜  HelloCargo tree             
.
├── Cargo.lock
├── Cargo.toml
├── src
│   └── main.rs
└── target
    ├── CACHEDIR.TAG
    └── debug
        ├── build
        ├── deps
        │   ├── HelloCargo-df20ee0cf9cc5b64
        │   └── HelloCargo-df20ee0cf9cc5b64.d
        ├── examples
        ├── HelloCargo
        ├── HelloCargo.d
        └── incremental
            └── HelloCargo-011kjb6sxrvh1
                ├── s-gyg8sfz5wq-1hyi1c6-16ixlnmc8l05bf26q7g0em353
                │   ├── 09dcn41b8350ez6e75honj68v.o
                │   ├── 2d10sna4o6u04tradnfzzaa92.o
                │   ├── 32ltz94n7vf7bj6p0fd1esgfl.o
                │   ├── 7250g7fhw71b7zl3xeofuy808.o
                │   ├── 79phbzp6l5q1atzu3fr2auezb.o
                │   ├── 8u43c87ozrbdg12qwnp8dyh9s.o
                │   ├── dep-graph.bin
                │   ├── query-cache.bin
                │   └── work-products.bin
                └── s-gyg8sfz5wq-1hyi1c6.lock

10 directories, 18 files
```

```shell
➜  HelloCargo cargo run        
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/HelloCargo`
Hello, world!
```

## `cargo check`

+ `cargo check` 可以快速检查代码确保其可以编译，但不产生实际的可执行文件。

##  `release build`

当项目最终准备好发布时，可以使用 `cargo build --release` 来优化编译项目。这会在 _target/release_ 而不是 _target/debug_ 下生成可执行文件。这些优化可以让 Rust 代码运行的更快，不过启用这些优化也需要消耗更长的编译时间。这也就是为什么会有两种不同的配置：一种是为了开发，你需要经常快速重新构建；另一种是为用户构建最终程序，它们不会经常重新构建，并且希望程序运行得越快越好。如果你在测试代码的运行时间，请确保运行 `cargo build --release` 并使用 _target/release_ 下的可执行文件进行测试。
