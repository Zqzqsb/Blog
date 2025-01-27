---
title: Golang Dependency
createTime: 2024-11-21
tags:
  - golang
author: ZQ
permalink: /golang/dependency/
---

讲述了`golang`的发展历史，现行范式和框架，核心要素。

<!-- more -->

## 历史

### `GoPath`

```shell
$GOPATH/
    src/   # 源代码目录
    pkg/   # 编译后的中间文件
    bin/   # 可执行文件
```

+ 默认会下载依赖包的最新版本
+ 所有包都会存放在 `$GOPATH/src` 下
+ 支持指定版本号(早期 Go 不支持版本管理)

**问题**

+ **依赖共享问题**  `$GOPATH` 下的依赖是全局共享的，多个项目可能依赖不同版本的同一个包，容易冲突。
+ **版本控制困难** 依赖包的版本管理较为原始，go get 总是获取最新版本，无法直接指定版本。
+ **手动管理麻烦** 需要手动管理 vendor 目录或使用工具，增加了额外的复杂性。
+ **不支持多模块** 一个项目只能在 $GOPATH/src 下，难以支持多个模块的开发。

### `go vendor`

**Vendor** 是 Go 项目的一种依赖管理机制：
+ 依赖的第三方包源码会被存储在项目的 vendor **目录** 中。
+ Go 编译器优先使用 vendor **目录** 中的依赖，而不是从 $GOPATH 或远程下载。

**查找顺序：**

编译器在编译时，会按照以下顺序查找依赖：

1. **当前包的 vendor 目录。**
2. **父目录的 vendor 目录。**
3. **$GOPATH/src。**
4. **$GOROOT/src。**

**复用性**

项目依赖被存储在 **Vendor 目录** 中，版本固定，团队成员只需拉取项目代码即可复现一致的依赖环境。
  
**问题**

1. **目录臃肿：** vendor 目录存储所有依赖的源码，导致项目体积较大。
2. **手动管理复杂：** 如果不使用工具，手动管理 vendor 目录是一个痛点。
3. **不够灵活：** 更新依赖版本需要额外操作，维护多个项目的依赖可能会有重复工作。
4. **与 GOPATH 的局限性相关：** Vendor 模式仍依赖于 GOPATH 工作区，不支持模块化开发。

## `go module`

现行的依赖管理方案，现代依赖管理三要素。
+ 依赖配置文件 : `go.mod`
+ 中心依赖库 ：`Proxy`
+ 本地工具 : `go get/mod`

### 特点

1. **脱离** $GOPATH**：** 项目可以放置在任何目录中，无需依赖 $GOPATH。
2. **依赖版本控制：** 通过 go.mod 文件管理模块依赖及其版本。
3. **语义化版本支持：** 使用语义化版本（Semantic Versioning, 如 v1.2.3）。
4. **依赖缓存：** 下载的依赖存储在本地 $GOPATH/pkg/mod 缓存中，加速构建。
5. **Proxy 支持：** 默认使用 https://proxy.golang.org 提高依赖解析和下载速度。

### `go.mod`文件

```go
module example.com/myproject  // 模块路径

go 1.20                       // 最低支持的 Go 版本

require (                     // 依赖的模块及其版本
    github.com/gin-gonic/gin v1.8.1
    golang.org/x/crypto v0.5.0
)

replace github.com/example/repo => ../local/repo // 替换模块路径
```

### 常用命令

```shell
go mod init example.com/myproject # 初始化一个项目

# 添加依赖
go get github.com/gin-gonic/gin@v1.8.1  # 指定版本
go get github.com/gin-gonic/gin         # 默认最新版本

# 升级
go get -u github.com/gin-gonic/gin          # 升级到最新版本
go get github.com/gin-gonic/gin@v1.7.0      # 升级到指定版本

# 清理
go mod tidy

# 下载
go mod download
```

### `Proxy`源

可以将环境变量添加到`.zshrc`中

```shell
export GOPROXY=https://goproxy.cn,direct
```

## 对比

| **特性**         | **Go Modules**                   | **GOPATH 模式**              | **Vendor 模式**              |
|------------------|----------------------------------|-----------------------------|-----------------------------|
| **依赖存储位置** | `$GOPATH/pkg/mod`               | `$GOPATH/src`               | 项目内 `vendor` 目录        |
| **版本管理**     | 支持语义化版本（`v1.2.3`）      | 版本不可控                  | 手动管理                   |
| **多模块支持**   | 支持                            | 不支持                      | 不支持                     |
| **依赖下载方式** | 支持 Proxy 缓存                | 全局依赖管理，速度较慢       | 需手动管理或使用工具        |
| **适用场景**     | 现代项目依赖管理               | 早期简单项目                | 简单项目或向后兼容          |