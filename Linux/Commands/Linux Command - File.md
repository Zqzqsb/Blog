---
title: Linux 命令 - 文件相关
createTime: 2024-8-19
author: ZQ
tags:
  - linux
permalink: /Linux/Command/File/
---

 linux文件相关命令。
 
<!-- more -->

## 概述

本文记录linux中文件，文本处理和日志相关的命令。

## `Tail`  `Head`

以 `Tail`为例。

+ `tail -n N filename` 显示末尾的`N`行
+ `tail -f N filename` 显示末尾的`N`行并且持续追踪文件的变化
+ `tail -c N filename` 显示末尾的`N`字节

## `less`

`less` 是一个功能强大的文件查看工具，用于按页查看文件内容，并且支持向前和向后滚动、搜索内容等功能。相比于 `more` 命令，`less` 提供了更多的交互式操作选项，使得查看大型文件更加方便和灵活。

1. **打开文件**：
    ```
    less filename
    ```
    这将打开指定文件，并显示文件内容。可以使用箭头键向上或向下滚动文件内容。
    
1. **向前翻页**：
    - 空格键：向前翻动一页。
    - Page Down：向前翻动一页。
    - 向下箭头：向前滚动一行。
    
1. **向后翻页**：
    - B：向后翻动一页。
    - Page Up：向后翻动一页。
    - 向上箭头：向后滚动一行。
    
1. **搜索内容**：
    - `/pattern`：搜索指定模式的文本，按下 `/` 后输入要搜索的内容，按 Enter 开始搜索。
    - `n`：在搜索结果中定位到下一个匹配项。
    - `N`：在搜索结果中定位到上一个匹配项。
    
1. **退出 less**：
    - `q`：退出 less 查看器。

## `grep`

`grep` 是一个强大的文本搜索工具，用于在文件中搜索指定模式的文本行，并将符合条件的行打印出来。`grep` 命令在 Linux 和 Unix 系统中被广泛应用，常用于日志分析、文本搜索、数据提取等场景。

### 基本使用

`grep pattern filename`

这将在指定的文件中搜索包含指定模式（pattern）的文本行，并将匹配的行打印出来。pattern 支持正则式。

### 搜索参数

+ `-r` 可以递归的在目录中搜索
+ `-i` 匹配时忽略大小写
+ `-n` 显示匹配的行号
+ `-c` 显示匹配的行数 而不是实际内容
+ `-v` 反向搜索

## `stat`

`stat filename`可以查看一个文件的详细信息

## `ls`

`ls -l filename` 这将显示文件的详细信息，包括文件大小、权限、所有者等。文件大小通常以字节为单位显示。

## `awk`

有专门的笔记章节讲解 `awk`。
