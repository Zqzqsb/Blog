---
title: String in Golang.
createTime: 2024-7-15
tags:
  - Golang
description: 笔记记录了Golang中的字符串。
permalink: /note/golang/string/
---
 笔记记录了Golang中的字符串。
<!-- more -->

## 概述

字符串是 UTF-8 字符的一个序列（当字符为 ASCII 码时则占用 1 个字节，其它字符根据需要占用 2-4 个字节）。UTF-8 是被广泛使用的编码格式，是文本文件的标准编码，其它包括 XML 和 JSON 在内，也都使用该编码。由于该编码对占用字节长度的不定性，Go 中的字符串里面的字符也可能根据需要占用 1 至 4 个字节（示例见第 4.6 节），这与其它语言如 C++、Java 或者 Python 不同（Java 始终使用 2 个字节）。Go 这样做的好处是不仅减少了内存和硬盘空间占用，同时也不用像其它语言那样需要对
使用 UTF-8 字符集的文本进行编码和解码。

字符串是一种值类型，且值不可变，即创建某个文本后你无法再次修改这个文本的内容；更深入地讲，字符串是字节的定长数组。

Go 支持以下 2 种形式的字面值：

- 解释字符串：

    该类字符串使用双引号括起来，其中的相关的转义字符将被替换，这些转义字符包括：
    
    - `
`：换行符
    - ``：回车符
    - `	`：tab 键
    - `\u` 或 `\U`：Unicode 字符
    - `\`：反斜杠自身
- 非解释字符串：
	该类字符串使用反引号括起来，支持换行，例如：
    
    ```go
      `This is a raw string 
` 中的 `
\` 会被原样输出。
    ```

和 C/C++不一样，Go 中的字符串是根据长度限定，而非特殊字符` `。

`string` 类型的零值为长度为零的字符串，即空字符串 `""`。

一般的比较运算符（`==`、`!=`、`<`、`<=`、`>=`、`>`）通过在内存中按字节比较来实现字符串的对比。你可以通过函数 `len()` 来获取字符串所占的字节长度，例如：`len(str)`。

字符串的内容（纯字节）可以通过标准索引法来获取，在中括号 `[]` 内写入索引，索引从 0 开始计数：

- 字符串 str 的第 1 个字节：`str[0]`
- 第 i 个字节：`str[i - 1]`
- 最后 1 个字节：`str[len(str)-1]`

**注意事项** 获取字符串中某个字节的地址的行为是非法的，例如：`&str[i]`。

**字符串拼接符 `+`**

两个字符串 `s1` 和 `s2` 可以通过 `s := s1 + s2` 拼接在一起。

`s2` 追加在 `s1` 尾部并生成一个新的字符串 `s`。

你可以通过以下方式来对代码中多行的字符串进行拼接：

```go
str := "Beginning of the string " +
	"second part of the string"
```

由于编译器行尾自动补全分号的缘故，加号 `+` 必须放在第一行。

拼接的简写形式 `+=` 也可以用于字符串：

```go
s := "hel" + "lo,"
s += "world!"
fmt.Println(s) //输出 “hello, world!”
```

## `Strings` 和 `Strconv`

作为一种基本数据结构，每种语言都有一些对于字符串的预定义处理函数。Go 中使用 `strings` 包来完成对字符串的主要操作。

- `Compare(a, b string) int`：比较两个字符串并返回整数结果，0 表示相等，-1 表示 a 小于 b，1 表示 a 大于 b。
- `Contains(s, substr string) bool`：检查字符串是否包含子字符串，返回 true 表示包含，false 表示不包含。
- `ContainsAny(s, chars string) bool`：检查字符串是否包含任何字符集中的字符，返回 true 表示包含，false 表示不包含。
- `ContainsRune(s string, r rune) bool`：检查字符串是否包含指定的 Unicode 码点，返回 true 表示包含，false 表示不包含。
- `Count(s, substr string) int`：计算子字符串在字符串中出现的次数，返回子字符串出现的次数。
- `EqualFold(s, t string) bool`：判断两个字符串在忽略大小写的情况下是否相等，返回 true 表示相等，false 表示不相等。
- `Fields(s string) []string`：根据空白字符分割字符串，返回子字符串的切片。
- `FieldsFunc(s string, f func(rune) bool) []string`：使用自定义函数根据条件分割字符串，返回子字符串的切片。
- `HasPrefix(s, prefix string) bool`：检查字符串是否以指定前缀开头，返回 true 表示有前缀，false 表示没有前缀。
- `HasSuffix(s, suffix string) bool`：检查字符串是否以指定后缀结尾，返回 true 表示有后缀，false 表示没有后缀。
- `Index(s, substr string) int`：返回子字符串在字符串中第一次出现的索引，若未找到则返回 -1。
- `IndexAny(s, chars string) int`：返回字符串中任一字符在字符集中第一次出现的索引，若未找到则返回 -1。
- `IndexByte(s string, c byte) int`：返回字节在字符串中第一次出现的索引，若未找到则返回 -1。
- `IndexFunc(s string, f func(rune) bool) int`：返回满足函数条件的第一个字符的索引，若未找到则返回 -1。
- `IndexRune(s string, r rune) int`：返回 Unicode 码点在字符串中第一次出现的索引，若未找到则返回 -1。
- `Join(a []string, sep string) string`：将字符串切片用指定分隔符连接，返回连接后的字符串。
- `LastIndex(s, substr string) int`：返回子字符串在字符串中最后一次出现的索引，若未找到则返回 -1。
- `LastIndexAny(s, chars string) int`：返回字符串中任一字符在字符集中最后一次出现的索引，若未找到则返回 -1。
- `LastIndexByte(s string, c byte) int`：返回字节在字符串中最后一次出现的索引，若未找到则返回 -1。
- `LastIndexFunc(s string, f func(rune) bool) int`：返回满足函数条件的最后一个字符的索引，若未找到则返回 -1。
- `Map(mapping func(rune) rune, s string) string`：返回将字符串中每个字符映射为新字符后的结果字符串。
- `Repeat(s string, count int) string`：返回重复指定次数后的新字符串。
- `Replace(s, old, new string, n int) string`：返回将字符串中前 n 个旧子字符串替换为新子字符串后的结果字符串。
- `ReplaceAll(s, old, new string) string`：返回将字符串中所有旧子字符串替换为新子字符串后的结果字符串。
- `Split(s, sep string) []string`：返回根据指定分隔符分割后的子字符串切片。
- `SplitAfter(s, sep string) []string`：返回根据指定分隔符分割后的子字符串切片，保留分隔符。
- `SplitAfterN(s, sep string, n int) []string`：返回根据指定分隔符分割后的最多 n 个子字符串切片，保留分隔符。
- `SplitN(s, sep string, n int) []string`：返回根据指定分隔符分割后的最多 n 个子字符串切片。
- `Title(s string) string`：返回将字符串中每个单词的首字母大写后的结果字符串。
- `ToLower(s string) string`：返回将字符串中的所有字母转换为小写后的结果字符串。
- `ToLowerSpecial(c unicode.SpecialCase, s string) string`：返回将字符串中的所有字母根据特殊规则转换为小写后的结果字符串。
- `ToTitle(s string) string`：返回将字符串中的所有字母转换为标题格式后的结果字符串。
- `ToTitleSpecial(c unicode.SpecialCase, s string) string`：返回将字符串中的所有字母根据特殊规则转换为标题格式后的结果字符串。
- `ToUpper(s string) string`：返回将字符串中的所有字母转换为大写后的结果字符串。
- `ToUpperSpecial(c unicode.SpecialCase, s string) string`：返回将字符串中的所有字母根据特殊规则转换为大写后的结果字符串。
- `Trim(s string, cutset string) string`：返回去掉字符串首尾指定字符集后的结果字符串。
- `TrimFunc(s string, f func(rune) bool) string`：返回去掉字符串首尾满足函数条件字符后的结果字符串。
- `TrimLeft(s string, cutset string) string`：返回去掉字符串左侧指定字符集后的结果字符串。
- `TrimLeftFunc(s string, f func(rune) bool) string`：返回去掉字符串左侧满足函数条件字符后的结果字符串。
- `TrimPrefix(s, prefix string) string`：返回去掉字符串前缀后的结果字符串。
- `TrimRight(s string, cutset string) string`：返回去掉字符串右侧指定字符集后的结果字符串。
- `TrimRightFunc(s string, f func(rune) bool) string`：返回去掉字符串右侧满足函数条件字符后的结果字符串。
- `TrimSpace(s string) string`：返回去掉字符串首尾空白字符后的结果字符串。
- `TrimSuffix(s, suffix string) string`：返回去掉字符串后缀后的结果字符串。
