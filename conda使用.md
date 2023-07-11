---
title: Conda的基本使用
categories: conda
date: 2022-7-11
cover: "封面.png"
description: "本文记录了conda的基本命令。"
---



## conda 使用

+ conda -V
+ conda info -e
+ conda create --name TestE python=3.8
+ conda remove -n TestE --all
+ conda activate TestE
+ conda deactivate
+ conda config --set auto_activate_base false
  + 取消自动激活base 使用系统自带python环境
