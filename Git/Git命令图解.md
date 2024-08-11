---
title: Git 命令图解
createTime: 2024-8-2
description: 本文参照了Learn Git Branch, 给出了git命令一些常用命令的图解。
tags:
  - hexo
author: ZQ
permalink: /git/graphIntro/
---
<br> 本文参照了Learn Git Branch, 给出了git命令一些常用命令的图解。
<!-- more -->

## git branch

创建一个新的分支。

## git switch

在分支之间切换。

## git merge {branch}

可以使用 `git merge` 命令将目标分支（即你想要合并的分支）的更改合并到当前分支。

**在合并之后，目标分支线将仍然得到保留。**
**在合并之后，当前分支会自动产生一次新的提交，这是分支合并后的结果。**
