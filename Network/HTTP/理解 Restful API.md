---
title: 理解 Restful API
createTime: 2026-2-2
author: ZQ
tags:
  - http
  - network
description: 理解 Restful API
permalink: /network/http/understand-restful-api/
---
 关于Http协议的发展历史。
 
<!-- more -->

## 深入理解 RESTful API 设计风格

> REST (Representational State Transfer) 是一种用于构建网络应用的架构风格，而非一个具体的标准或协议。它利用 HTTP 协议的现有特性（如方法和状态码），通过一种清晰、可预测的方式来组织和暴露服务。一个遵循 REST 原则的 API 被称为 RESTful API。

---

## 1. 核心概念：解读 "Representational State Transfer"

> 要理解 REST，最有效的方法是拆解其名称的三个核心组成部分：资源 (Resource)、表现层 (Representation) 和状态转化 (State Transfer)。这三个概念共同定义了客户端与服务器如何通过网络进行交互。

### 1.1. 资源 (Resource)

> **资源是 REST 架构的核心，它是网络上任何可被命名的信息或实体。**

-   **定义**: 资源可以是一份文档、一张图片、一个用户对象，甚至是一种服务（如“天气预报服务”）。每个资源都通过一个唯一的 URI (统一资源标识符) 来定位。
-   **关键点**: URI 标识的是资源本身，而不是它的具体格式。例如，`/users/123` 这个 URI 代表的是 ID 为 123 的用户，而不是这个用户的 JSON 或 XML 数据。

### 1.2. 表现层 (Representation)

> **表现层是资源在特定时刻的状态快照，以某种格式呈现出来。**

-   **定义**: 同一个资源可以有多种表现形式。例如，用户信息可以表现为 JSON、XML 或 HTML 格式。客户端和服务器通过内容协商 (Content Negotiation) 来决定使用哪种表现层。
-   **实现**: 客户端在 HTTP 请求头中使用 `Accept` 字段来声明它能理解的格式 (如 `Accept: application/json`)，服务器则在响应头中使用 `Content-Type` 字段来指明返回数据的实际格式 (如 `Content-Type: application/json`)。

### 1.3. 状态转化 (State Transfer)

> **状态转化指客户端通过 HTTP 方法对服务器上的资源进行操作，从而导致资源状态发生改变的过程。**

-   **定义**: 由于 HTTP 是无状态协议，所有应用状态都存储在服务器端。客户端通过发送 HTTP 请求来驱动服务器上资源状态的“转化”。
-   **实现**: 客户端使用标准的 HTTP 方法（动词）来表达其意图，例如 `GET` (获取)、`POST` (创建)、`PUT` (更新)、`DELETE` (删除)。服务器执行相应操作，改变资源状态，并将结果返回给客户端。

---

## 2. RESTful API 的设计原则

> 一个真正符合 REST 风格的 API 需要遵循以下核心设计原则，这些原则确保了系统的可伸缩性、简单性和可靠性。

-   **客户端-服务器分离 (Client-Server)**: 客户端和服务器的职责严格分离。UI 和数据存储可以独立演进，提高了系统的灵活性和可移植性。
-   **无状态 (Stateless)**: 每个来自客户端的请求都必须包含处理该请求所需的所有信息。服务器不应在两次请求之间存储任何关于客户端的上下文信息。这简化了服务器的设计，并提高了可伸缩性。
-   **可缓存 (Cacheable)**: 服务器的响应应明确标识自身是否可被缓存。这允许客户端或中间代理缓存响应，从而减少延迟，提高性能。
-   **统一接口 (Uniform Interface)**: 这是 REST 最核心的原则，它简化并解耦了架构。统一接口包含四个子约束：
    1.  **基于资源**: 通过 URI 标识资源。
    2.  **通过表现层操作资源**: 客户端通过资源的表现层（如 JSON）来修改资源，而不是直接访问服务器内部实现。
    3.  **自描述消息**: 每个请求和响应都包含足够的信息来描述如何处理它，例如使用 `Content-Type` 定义媒体类型。
    4.  **超媒体作为应用状态的引擎 (HATEOAS)**: 响应中应包含链接，指导客户端如何进行下一步操作。例如，获取一个账户信息的响应可以包含“存款”、“取款”等操作的链接。
-   **分层系统 (Layered System)**: 客户端通常不知道它连接的是最终服务器还是中间代理。这允许在中间层部署负载均衡、缓存或安全策略，而不影响客户端和服务器的交互。

---

## 3. HTTP 方法与 CRUD 操作

> RESTful API 优雅地将 HTTP 方法映射到资源的增删改查 (CRUD) 操作上，使得 API 的行为直观且可预测。

| HTTP 方法 | 操作     | 描述                                     |
| :-------- | :------- | :--------------------------------------- |
| `GET`     | 读取 (Read)   | 从服务器获取一个或多个资源。             |
| `POST`    | 创建 (Create) | 在服务器上创建一个新资源。                 |
| `PUT`     | 更新 (Update) | 完整替换服务器上的一个已有资源。         |
| `PATCH`   | 部分更新 (Update) | 对服务器上的资源进行部分修改。           |
| `DELETE`  | 删除 (Delete) | 从服务器上删除一个资源。                 |

---

## 4. 常见设计误区与最佳实践

> 设计 RESTful API 时，应避免将 URI 视为行为调用，而应始终将其视为资源的定位符。

### 误区：URI 中包含动词

因为资源是名词，所以 URI 中应避免使用动词。操作资源的“动词”应该由 HTTP 方法来承担。

-   **错误示例**: `GET /posts/show/1`
-   **正确实践**: `GET /posts/1` (动词 `show` 由 `GET` 方法体现)

### 实践：将非 CRUD 操作名词化

如果某个操作无法直接用标准的 HTTP 方法表示（如“汇款”），应将其视为一种资源。

-   **错误示例**: `POST /accounts/1/transfer/500/to/2`
-   **正确实践**: 将“交易”(`transfer`) 视为一个新资源。客户端通过 `POST` 请求创建一个“交易”资源。

```http
POST /transactions HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "from_account": "/accounts/1",
  "to_account": "/accounts/2",
  "amount": 500.00
}
```