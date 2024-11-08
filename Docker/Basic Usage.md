---
title: Basic Usage of Docker
createTime: 2022-7-11
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/docker_%E4%BD%BF%E7%94%A8/%E5%B0%81%E9%9D%A2.png
description: 本文记录了docker的基本命令。
tags:
  - docker
author: ZQ
permalink: /docker/usage/
---
![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/docker_%E4%BD%BF%E7%94%A8/%E5%B0%81%E9%9D%A2.png)
 本文记录了docker的基本命令。
<!-- more -->

## docker 使用

- docker command --help
- docker images
  - 显示所有本地镜像
- docker search mysql --filter-stars=3000
  - 搜索
- docker pull mysql
  - 下载镜像
- docker rmi -f $(docker images -aq)
  - 删除全部镜像
- docker run [optional] image
  - -name 容器名
  - -d 后台
  - -it 交互
  - -p 容器端口: 容器端口
  - -P 随机端口
- docker ps(列出所运行的容器)
  - -a -1
- exit / Ctrl + P + Q
- docker rm -f $(docker ps -aq)
- docker logs - tf --tail 10 (containerid)
