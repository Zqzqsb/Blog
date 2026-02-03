---
title: Macos - Startup
createTime: 2024-11-5
author: ZQ
permalink: /Macos/Startup/
---

最近安装了一台黑苹果，想记录一下从零开始配置可用的过程。 并且在这一过程中学习一下`bash`相关的知识。于是有了配置系列的博客。

<!-- more -->

## 前言

首先炫耀一下自己的黑苹果。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Configuration/Startup/MacPro.png)

## 软件准备

### 基本

+ Chrome
+ BaiduDisk
+ Wechat

### 编程

+ Vsc
+ Terminus
+ Alacrity
+ Xcode Command line Tool
+ Oss Browser
+ Zellij

### 效率

+ Homebrew
+ Raycast
+ Ishot
+ Snippate
+ Rime

### 文档

+ Typora
+ Obsidian

### 虚拟组网

+ zerotier

首先解决网络问题，确保上面的常用软件处于可用的状态。

## Rime 配置

输入法是必须要预先配置的环节,可谓万物之始。

### 下载

```shell
brew install --cask squirrel
```

### 配置

由于我使用的全拼，所以直接抄作业 , [雾凇拼音](https://github.com/iDvel/rime-ice)。

```shell
git clone  https://github.com/iDvel/rime-ice.git
```

```shell
cp -r rime-ice/* ~/Library/Rime/
```

去`~/Library/Rime`中找到`defaul.yaml`,注释掉自己不需要的方案，然后重新部署即可。

## Raycast 配置

Raycast是自带的聚焦搜索的绝佳的替代方案，需要做简单配置以贴合自己的使用习惯。

基于界面做配置比较简单，主要是一些快捷键，根据使用习惯来就可以。

## `zsh`配置

主要基于`oh-my-zsh`做一些配置。

```shell
# --------------------- oh-my-zsh ---------------
## 将zsh的历史和缓存文件统一管理ZSH主目录中
export ZSH=$HOME/.oh-my-zsh
HISTFILE="${ZSH}/.zsh_history"
ZSH_COMPDUMP="${ZSH}/cache/.zcompdump-${SHORT_HOST}-${ZSH_VERSION}"

## 主题
ZSH_THEME="jonathan"

## 插件列表
# git : git相关
# fzf-tab : 增强补全
# zsh-syntax-highlighting : 高亮
# zsh-autosuggestions : 行内补全
# zsh-vi-mode : 行内vim模式
# colored-man-pages : 高亮man手册
# zsh-bubble : 执行特效

plugins=(git fzf-tab zsh-syntax-highlighting zsh-autosuggestions zsh-vi-mode colored-man-pages zsh-bubble)

source $ZSH/oh-my-zsh.sh

# --------------------- zsh --------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=blue'

# --------------------- general --------------------
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### `Fuzzy-Shell`

终端效率工具。

```shell
# clone the repo
git clone https://github.com/Albert26193/fuzzy-shell.git
 
# install on Mac (no sudo)
cd fuzzy-shell && bash install/install.sh
```

安装之后会在`.zshrc`中添加

```shell
#------------------- fuzzy-shell -------------------
source "${HOME}/.fuzzy_shell/scripts/export.sh"
alias "fs"="fuzzy --search" # 模糊搜索
alias "fj"="fuzzy --jump" # 模糊跳转
alias "fe"="fuzzy --edit" # 模糊搜索并编辑
alias "hh"="fuzzy --history" # 模糊历史
```

## `zerotier`组网

为了和自建行星节点的`vpn`通信。需要替换`zerotier`的`planet`文件，之后加入网络。

参考这个[仓库](https://github.com/xubiaolin/docker-zerotier-planet)

1. 进入 `/Library/Application\ Support/ZeroTier/One/` 目录，并替换目录下的 `planet` 文件
2. 重启 ZeroTier-One：`cat /Library/Application\ Support/ZeroTier/One/zerotier-one.pid | sudo xargs kill`
3. 加入网络 `zerotier-cli join` 网络 `id`
4. 管理后台同意加入请求
5. `zerotier-cli peers` 可以看到 `planet` 角色










