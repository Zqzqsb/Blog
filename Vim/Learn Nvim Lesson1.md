---
title: Learn Nvim Lesson1
createTime: 2024-9-2
author: ZQ
tags:
  - vim
description: 记录了学习nvim第一课学到的内容
permalink: /vim/lesson1/
---

## basic command structure
verb + conduct + obj

## v / (d) / (c)

+ v i t 选中当前tab 内(in) 的所有内容
+ v a t 选中当前tab的所有内容
+ v i "tag" 选中当前tag闭包内的所有内容
+ v a "tag" 选中当前tag中的所有内容 包括tag符号
+ v i w 选中当前word

## conduct

+ a means all
+ i means inside

## object

+ t means current tag
+ w means current word
+ () {} [] <>
+ p means current paragraph
+ b/B means current block

## common hotkeys

### choose

+ V: select current line

### move

+ $: jump to end
+ ^: jump to start(first non empty string)
+ 0: jump to start
+ {number}gg: jump to {number} line
+ {number}G: jump to {number} line
+ gg: jump to head of file
+ G: jump to tail of file
+ M: jump to middle of file
+ { : move to prev empty line
+ } : move to next empty line
+ * : highlight current word and jump
+ n: to next highlight word
+ N: to prev highlight word
+ zt: move highlight line to top
+ zb: move highlight line to bottom
+ zz: move highlight line to middle

### edit

+ 3 + obj: v / d / c
+ 2 no obj: x / s
+ i: insert
+ I : insert on head
+ a: append
+ A: append on tail
+ s: substitute
+ o : open a new line
+ O : open a new line before
+ ciw / diw
+ how to choose a function: {number}gg + V + %
+ J: join line
+ C: substitute to end of line
+ D: delete to end of line
+ cc: substitute the whole line
+ dd: delete the whole line
+ =G: pretty code below

### window

+ ctrl + w : trigger
+ trigger + h/j/k/l: split pane and move
+ trigger + o: only one group
+ trigger + w: jump to another pane
+ : tabonly[tabo]: only one ta

### misc

- gd: go to definition
- gh: go to reference
- K: hover 

### plugin

- w: changed origin key! --> trigger easy motion plugin, w + {you want to go}
- u: undo
- ctrl + r : redo
- . : repeat edit
- ; : repeat find

## next steps!

+ yank and paste
+ command mode
+ micro
+ complex operations