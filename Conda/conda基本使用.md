---
title: Conda的基本使用
createTime: 2022-7-11
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/conda_%E4%BD%BF%E7%94%A8/%E5%B0%81%E9%9D%A2.png
description: 本文记录了conda的基本命令。
tags:
  - conda
author: ZQ
permalink: /conda/usage/
---
![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/conda_%E4%BD%BF%E7%94%A8/%E5%B0%81%E9%9D%A2.png)
<br> 本文记录了conda的基本命令。
<!-- more -->

## conda 使用

- conda -V
  - 查看 conda 版本
- conda info -e
  - 查看当前已有的 conda 环境
- conda create --name TestE python=3.8
  - 创建一个新的 conda 环境
- conda remove -n TestE --all
  - 根据名字删除一个 conda 环境
- conda activate TestE
  - 激活一个 conda 环境
- conda deactivate
  - 取消 conda 激活 回退到 base 或者系统环境
- conda config --set auto_activate_base false
  - 取消自动激活 base 使用系统自带 python 环境
