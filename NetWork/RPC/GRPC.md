---
title: Grpc 
createTime: 2024-12-17
author: ZQ
tags:
  - rpc
  - network
permalink: /network/rpc/grpc/
---

描述了`gRPC`的概念已经它和`http/2`的关系。

<!-- more -->

## `grpc`概述

**gRPC**（**g** Remote Procedure Call）是一种 **高性能、开源的远程过程调用（RPC）框架**，由 **Google** 开发并开源，基于 **HTTP/2** 协议和 **Protocol Buffers**（protobuf）进行数据序列化。

gRPC 允许客户端和服务器之间通过网络进行函数调用，就像调用本地函数一样，封装了底层网络通信的复杂性。

## `grpc`利用`h2`作为传输层

**多路复用**

- HTTP/2 允许在同一个 TCP 连接上同时发送多个请求和响应，互不干扰。
- gRPC 利用这一特性，让多个 RPC 请求在同一连接上复用，实现高效通信，避免了 HTTP/1.1 中 **“队头阻塞”** 的问题（在 HTTP/2 层面，而非 TCP 层面）。

**流式传输**

- HTTP/2 支持 **双向流式传输**，gRPC 基于此实现了多种通信模式：
    - **普通 RPC**：请求和响应一次性完成。
    - **服务端流式**：服务端连续发送数据流给客户端。
    - **客户端流式**：客户端连续发送数据流给服务端。
    - **双向流式**：客户端和服务端可以同时发送数据流，像 WebSocket 一样。

**头部压缩**

- HTTP/2 使用 **HPACK** 算法压缩请求和响应头部，减少传输开销。
- gRPC 中的元数据（Metadata）通过头部传输，HTTP/2 的压缩特性使 gRPC 传输更高效。

**二进制帧**

- HTTP/2 使用二进制帧传输数据，而不是 HTTP/1.1 的纯文本格式。
- gRPC 基于 HTTP/2 的二进制传输，结合 **Protocol Buffers**（protobuf）进行高效的数据序列化与反序列化，进一步提升了性能。

**长连接**

- HTTP/2 采用长连接机制，一个连接可以复用，避免了频繁建立和关闭连接的开销。
- gRPC 基于 HTTP/2 的长连接，可以高效地维护多个并发请求的通信通道。

## `grpc`调用过程

```diff
+-----------------------+
|     gRPC 应用层       |   <- gRPC 定义服务和方法，处理逻辑
+-----------------------+
|    HTTP/2 传输层      |   <- 提供多路复用、流式传输等能力
+-----------------------+
|    TCP/网络层         |   <- 负责底层数据包传输
+-----------------------+
```

gRPC 请求发送时，会形成一个基于 HTTP/2 的消息，具体如下：

- **HTTP 方法**：`POST`
- **路径**：`/ServiceName/MethodName`  
    例如：`/Greeter/SayHello`
- **Content-Type**：`application/grpc`（表示这是一个 gRPC 请求）
- **消息体（Body）**：
    - 经过 Protocol Buffers 序列化的二进制数据。

**示例 HTTP 请求头**（gRPC 格式）：

```makefile
POST /Greeter/SayHello HTTP/2
Host: example.com
Content-Type: application/grpc
TE: trailers
```

### 为什么不使用`GET`

gRPC 选择 `POST` 而非 `GET` 的主要原因是：

1. **数据放在 Body 中**：

    - gRPC 需要发送复杂的、二进制序列化后的数据，`GET` 方法无法携带请求体（HTTP 标准限制）。
    - `POST` 可以将数据放在请求的 Body 中，这是最合适的选择。
3. **支持流式传输**：
    
    - gRPC 允许请求和响应中包含 **多条消息流**（如双向流式 RPC）。
    - `POST` 方法天然适合支持这种长时间、数据流式传输的场景，而 `GET` 不具备这种能力。
3. **幂等性要求**：
    
    - HTTP 中，`GET` 通常被认为是 **幂等** 的（不会改变服务器状态），适合查询操作。
    - gRPC 的 RPC 调用可能涉及状态变更和复杂业务逻辑，使用 `POST` 更符合语义。