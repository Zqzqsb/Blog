---
title: Guessing Game by Rust
createTime: 2024-7-28
tags:
  - Rust
description: 使用Rust实现了一个小的猜数游戏。
---
 使用Rust实现了一个小的猜数游戏。
<!-- more -->

## 读入输入

```rust
use std::io;

fn main() {
    println!("Guess the number!");

    println!("Please input your guess.");

    let mut guess = String::new();

    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");

    println!("You guessed: {}", guess);
}
```

为了获取用户输入并打印结果作为输出，我们需要将 `io`输入/输出库引入当前作用域。`io` 库来自于标准库，也被称为 `std`：

默认情况下，Rust 设定了若干个会自动导入到每个程序作用域中的标准库内容，这组内容被称为 _预导入（prelude）_ 内容。你可以在[标准库文档](https://doc.rust-lang.org/std/prelude/index.html)中查看预导入的所有内容。

如果你需要的类型不在预导入内容中，就必须使用 `use` 语句显式地将其引入作用域。`std::io` 库提供很多有用的功能，包括接收用户输入的功能。

### 测试

```shell
➜  GuessingGame cargo run
   Compiling GuessingGame v0.1.0 (/home/zq/Projects/Learning/LearnRust/Projects/GuessingGame)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.07s
     Running `target/debug/GuessingGame`
Guess the number!
Please input your guess.
10
You guessed: 10
```

## 处理异常输入

```rust
let guess: u32 = match guess.trim().parse() {
	Ok(num) => num,
	Err(_) => continue,
};
```

 如果当前输入不能被正常转换，就`continue`这次 `loop`。

## 使用外部依赖

在`Cargo.toml`中添加

```toml
[dependencies]
rand = "0.8.5"
```

在 `main.rs`使用`rand` 并创建随机数

```rust
let secret_number = rand::thread_rng().gen_range(1..=100);
```

## 完整代码

```rust
use std::io;
use std::cmp::Ordering;
use rand::Rng;

fn main() {
    let secret_number = rand::thread_rng().gen_range(1..=100);
    println!("Guess the number!");

    loop {
        println!("Please input your guess.");

        let mut guess = String::new();
        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");

        println!("You guessed: {}", guess);

        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too big!"),
            Ordering::Equal => {
                println!("You win!");
                break;
            }
        }
    }
}

```
