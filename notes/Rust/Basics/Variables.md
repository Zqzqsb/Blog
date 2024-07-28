---
title: Variables and their variabilities.
createTime: 2024-7-28
tags:
  - Rust
description: 记录rust中的变量及它们的可变性。
---
<br> 记录rust中的变量及它们的可变性。
<!-- more -->

## 默认不可变性

```rust
fn main() {
    let x = 5;
    println!("The value of x is: {x}");
    x = 6;
    println!("The value of x is: {x}");
}
```

这段程序会引发编译错误。因为对`x`进行了二次赋值。可以使用`mut`(stands for mutable)关键字申明变量的可变性。

```rust
fn main() {
    let mut x = 5;
    println!("The value of x is: {x}");
    x = 6;
    println!("The value of x is: {x}");
}
```

## 常量

类似于不可变变量，_常量 (constants)_ 是绑定到一个名称的不允许改变的值，不过常量与变量还是有一些区别。

首先，不允许对常量使用 `mut`。常量不光默认不可变，它总是不可变。声明常量使用 `const` 关键字而不是 `let`，并且 _必须_ 注明值的类型。

常量可以在任何作用域中声明，包括全局作用域，这在一个值需要被很多部分的代码用到时很有用。

最后一个区别是，常量只能被设置为常量表达式，而不可以是其他任何只能在运行时计算出的值。

+ 一个申明常量的例子

```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
```

Rust 对常量的命名约定是在**单词之间使用全大写加下划线**(Big Snake Case)。

## 覆盖(隐藏)

很常见的变量覆盖行为，允许多次定义实现对过去的变量的覆盖。

```rust
fn main() {
    let x = 5;
    let x = x + 1;
    {
        let x = x * 2;
        println!("The value of x in the inner scope is: {x}");
    }
    println!("The value of x is: {x}");
}
```

隐藏与将变量标记为 `mut` 是有区别的。当不小心尝试对变量重新赋值时，如果没有使用 `let` 关键字，就会导致编译时错误。通过使用 `let`，我们可以用这个值进行一些计算，不过计算完之后变量仍然是不可变的。

`mut` 与隐藏的另一个区别是，当再次使用 `let` 时，实际上创建了一个新变量，**我们可以改变值的类型，并且复用这个名字**。

例如，假设程序请求用户输入空格字符来说明希望在文本之间显示多少个空格，接下来我们想将输入存储成数字（多少个空格）：

```rust
    let spaces = "   ";
    let spaces = spaces.len();
```

上面这个例子是正确，但下面的写法是错误的，因为我们不能像`python`一般灵活的改变变量的类型。

```rust
    let mut spaces = "   ";
    spaces = spaces.len();
```

本质上`shadow`机制是为了过度重新定义新的变量。比如在`c++`中实现中该需求，就需要

```cpp
	string spaces = "    ";
	int lenSpaces = spaces.length();
```
