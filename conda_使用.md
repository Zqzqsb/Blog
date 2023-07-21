---
title: Conda的基本使用
categories: conda
date: 2022-7-11
cover: "封面.png"
description: "本文记录了conda的基本命令。"
---



## conda 使用

+ conda -V
  + 查看conda 版本
+ conda info -e
  + 查看当前已有的conda环境
+ conda create --name TestE python=3.8
  + 创建一个新的conda环境
+ conda remove -n TestE --all
  + 根据名字删除一个conda环境
+ conda activate TestE
  + 激活一个conda环境
+ conda deactivate
  + 取消conda激活 回退到base或者系统环境
+ conda config --set auto_activate_base false
  + 取消自动激活base 使用系统自带python环境
