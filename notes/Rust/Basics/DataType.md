---
title: Datatypes in rust.
createTime: 2024-7-28
tags:
  - Rust
description: rust中数据类型。
---
<br> rust中数据类型。
<!-- more -->

## 概述

在 Rust 中，每一个值都属于某一个 **数据类型**（_data type_），这告诉 Rust 它被指定为何种数据，以便明确数据处理方式。我们将看到两类数据类型子集：标量（scalar）和复合（compound）。

### 标量

**标量**（_scalar_）类型代表一个单独的值。Rust 有四种基本的标量类型：整型、浮点型、布尔类型和字符类型。你可能在其他语言中见过它们。让我们深入了解它们在 Rust 中是如何工作的。

### 整型

**整数** 是一个没有小数部分的数字。我们在第二章使用过 `u32` 整数类型。该类型声明表明，它关联的值应该是一个占据 32 比特位的无符号整数（有符号整数类型以 `i` 开头而不是 `u`）。表格 3-1 展示了 Rust 内建的整数类型。我们可以使用其中的任一个来声明一个整数值的类型。

|长度|有符号|无符号|
|---|---|---|
|8-bit|`i8`|`u8`|
|16-bit|`i16`|`u16`|
|32-bit|`i32`|`u32`|
|64-bit|`i64`|`u64`|
|128-bit|`i128`|`u128`|
|arch|`isize`|`usize`|

整型是以补码存储的。

可以使用下表的任何一种形式编写数字字面值。请注意可以是多种数字类型的数字字面值允许使用类型后缀，例如 `57u8` 来指定类型，同时也允许使用 `_` 做为分隔符以方便读数，例如`1_000`，它的值与你指定的 `1000` 相同。

|数字字面值|例子|
|---|---|
|Decimal (十进制)|`98_222`|
|Hex (十六进制)|`0xff`|
|Octal (八进制)|`0o77`|
|Binary (二进制)|`0b1111_0000`|
|Byte (单字节字符)(仅限于`u8`)|`b'A'`|

### 浮点型

Rust 也有两个原生的 **浮点数**（_floating-point numbers_）类型，它们是带小数点的数字。Rust 的浮点数类型是 `f32` 和 `f64`，分别占 32 位和 64 位。默认类型是 `f64`，因为在现代 CPU 中，它与 `f32` 速度几乎一样，不过精度更高。所有的浮点型都是有符号的。

一个定义浮点数的实例

```rust
fn main() {
    let x = 2.0; // f64
    let y: f32 = 3.0; // f32
}
```

浮点数采用 IEEE-754 标准表示。`f32` 是单精度浮点数，`f64` 是双精度浮点数。

### 数值运算

+ 常见的数值运算，没什么特殊的。

```rust
fn main() {

// addition
    let sum = 5 + 10;

    // subtraction
    let difference = 95.5 - 4.3;

    // multiplication
    let product = 4 * 30;

    // division
    let quotient = 56.7 / 32.2;
    let truncated = -5 / 3; // 结果为 -1

    // remainder
    let remainder = 43 % 5;
}
```

### 布尔型

```rust
fn main() {
    let t = true;
    let f: bool = false; // with explicit type annotation
}
```

### 字符型

```rust
fn main() {
    let c = 'z';
    let z: char = 'ℤ'; // with explicit type annotation
    let heart_eyed_cat = '😻';
}
```

### 复合类型

**复合类型**（_Compound types_）可以将多个值组合成一个类型。Rust 有两个原生的复合类
型：元组（tuple）和数组（array）。

**元组**

元组是一个将多个其他类型的值组合进一个复合类型的主要方式。元组长度固定：一旦声明，其长度不会增大或缩小。

我们使用包含在圆括号中的逗号分隔的值列表来创建一个元组。元组中的每一个位置都有一个类型，而且这些不同值的类型也不必是相同的。这个例子中使用了可选的类型注解：

```rust
fn main() {
    let tup: (i32, f64, u8) = (500, 6.4, 1);
}
```

可以通过解构将数组赋值到变量

```rust
fn main() {
    let tup = (500, 6.4, 1);
    let (x, y, z) = tup;
    println!("The value of y is: {y}");
}
```

也可以通过索引的方式访问

```rust
fn main() {
    let x: (i32, f64, u8) = (500, 6.4, 1);
    let five_hundred = x.0;
    let six_point_four = x.1;
    let one = x.2;
}
```

> 不带任何值的元组有个特殊的名称，叫做 **单元（unit）** 元组。这种值以及对应的类型都写作 `()`，表示空值或空的返回类型。如果表达式不返回任何其他值，则会隐式返回单元值。

**数组**

另一个包含多个值的方式是 **数组**（_array_）。与元组不同，数组中的每个元素的类型必须相同。Rust 中的数组与一些其他语言中的数组不同，Rust 中的数组长度是固定的。数组是可以在**栈** (stack) 上分配的已知固定大小的单个内存块。

一个定义数组的例子，将数组的值写成在方括号内，用逗号分隔：

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];
	let months = ["January", "February", "March", "April", "May", "June", "July","August", "September", "October", "November", "December"];
}
```

可以像这样编写数组的类型：在方括号中包含每个元素的类型，后跟分号，再后跟数组元素的数量。

```rust
	let a: [i32; 5] = [1, 2, 3, 4, 5];
```

还可以通过在方括号中指定初始值加分号再加元素个数的方式来创建一个每个元素都为相同值的数组：

```rust
	let a = [3; 5];
```

变量名为 `a` 的数组将包含 `5` 个元素，这些元素的值最初都将被设置为 `3`。这种写法与 `let a = [3, 3, 3, 3, 3];` 效果相同，但更简洁。

可以通过索引访问数组元素。

```rust
fn main() {
    let a = [1, 2, 3, 4, 5];
    let first = a[0];
    let second = a[1];
}
```

在这个例子中，叫做 `first` 的变量的值是 `1`，因为它是数组索引 `[0]` 的值。变量 `second` 将会是数组索引 `[1]` 的值 `2`。

当遭遇运行时的`out of range`访问时，`rust` 程序会引发`panic` 而直接退出。
