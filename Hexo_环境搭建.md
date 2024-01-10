---
title: Hexo*Butterfly 并使用nginx做静态代理
categories:
  - 博客建设
date: 2022-2-3
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/%E7%AE%97%E6%B3%95/Hexo_%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA/%E5%B0%81%E9%9D%A2.jpg
description: 本文介绍了hexo博客搭建的过程。
tags:
  - hexo
---

# 安装hexo框架并且使用nginx做静态代理

## 安装git

```shell
yum install git
git --version
```

## 下载nodejs 改名 并建立链接

```shell
cd /
mkdir Apps 
cd /Apps

wget https://nodejs.org/dist/v14.16.1/node-v14.16.1-linux-x64.tar.xz    
tar xf node-v14.16.1-linux-x64.tar.xz

mv node-v14.16.1-linux-x64 nodejs
sudo ln -s /Apps/nodejs/bin/npm /usr/local/bin/
sudo ln -s /Apps/nodejs/bin/node /usr/local/bin/
```

## 安装 n

```shell
npm install -g n
```

## 安装hexo  建立软链接

```shell
sudo npm install hexo-cli -g
sudo ln -s /Apps/nodejs/lib/node_modules/hexo-cli/bin/hexo /usr/local/bin/hexo
```

## 测试

```shell
node -v
npm -v
hexo -v
```

## 创建hexo目录  初始化 安装主题和渲染器 生成静态public目录

```shell
mkdir hexo 
cd hexo
hexo init

git clone -b master https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
npm install hexo-renderer-pug hexo-renderer-stylus --save

hexo g
```

## 安装nginx

```shell
yum install -y nginx
```

## 配置nginx 在/etc/nginx/nignx.conf 中修改root的位置

## 在nignx.conf 中配置ssl


```shell
nginx -s stop/reload
nginx # 直接启动
```

