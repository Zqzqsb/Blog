---
title: Build Blog Site In CI Pipeline
createTime: 2025-1-8
tags:
  - jenkins
  - SSG
  - Blog
author: ZQ
permalink: /blog/ci/
---

本文介绍了个人 `Blog`仓库的自动打包和发布过程，利用`github actions` 和 `jenkins ci`来实现自动化构建。

<!-- more -->

## 网络拓扑

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Blog/SSG%20CI/pipeline.png)

## `Jenkins` 搭建

### 通过`docker` 安装

**`docker-compose.yml`**

```yml
version: "3.8"

services:
  jenkins:
    build: .
    container_name: jenkins
    user: root
    ports:
      - "8567:8080" ## web 接口
      - "50000:50000"
    volumes:
      - ./jenkins_home:/var/jenkins_home ## 挂载 jenkins_home到当前目录 而非docker 卷中
      - /var/run/docker.sock:/var/run/docker.sock
      - ./.ssh:/root/.ssh ## 容器需要的密钥
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false ## 跳过启动引导
```

**`Dockerfile`**

构建时在容器中安装必要的依赖

```dockerfile
FROM jenkins/jenkins:lts
USER root

# 安装 Node.js 和 rsync
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs rsync

# 确认 Node.js 和 rsync 安装成功
RUN node -v && npm -v && rsync --version
```

### `Jenkins` 配置

**网络**

将网络通过`ngnix` 反向代理以确保可以进行互联网访问。

**用户**

在全局安全配置中选择用户策略为`jenkins`专用用户数据库。之后便可以分配用户。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Blog/SSG%20CI/user.png)

**插件**

安装三个插件

- `git plugin`
- `github plugin`
- `Chinese simplify plugin`

**Job**

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Blog/SSG%20CI/trigger.png)

创建`job`，使用远程触发。自行编写构建步骤。

## `github actions`

位于`.github/workflow` 下的配置文件。

```yml
name: Trigger Jenkins Build

on:
  push:
    branches:
      - master # 仅当推送到 `master` 分支时触发
  workflow_dispatch: # 允许手动触发

jobs:
  trigger-jenkins-build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Trigger Jenkins build
        run: |
          curl -v -X GET "${JENKINS_URL}/job/GenBlog/build?token=${API_TOKEN}"
        env:
          JENKINS_URL: https://jenkins.zqzqsb.cn
          API_TOKEN: ${{ secrets.JENKINS_API_TOKEN }} ## 在仓库的secrets属性中配置相关变量
```

## 构建相关

**工作目录**

创建好`jenkins  job` 之后，`jenkins_home/workspace/` 目录下会出现一个和项目同名的工作目录，将需要构建的项目放在该该目录中，赋予合适的权限。

编写一个构建脚本，在`jenkins pipeline`中只需要调用该脚本即可。

```bash
# 在本地生成好渲染好的目录
function GenBlogDist()
{
    cd ./blog && git pull && cd ..

    rm -rf ./docs/* && cp -r ./blog/* ./docs/
    cp ./README.md ./docs/

    npm run docs:build
}

# 将目录推送到博客服务器
function PushDistToServer()
{
    local LocalDist="./docs/.vuepress/dist"
    local RemoteDir="/WorkSpace/"
    local RemoteHost="BlogServer"

    if [ "$(ls -A ${LocalDist})" ]; then
        echo "LocalDist is not empty, starting rsync..."
        rsync --quiet -avz --delete "$LocalDist" "$RemoteHost:$RemoteDir"
    else
        echo "Local Dir is empty, nothing to push."
    fi
}

GenBlogDist && PushDistToServer
echo "Done!"
```
