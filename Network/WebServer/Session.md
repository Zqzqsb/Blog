---
title: Session
createTime: 2025-1-27
author: ZQ
tags:
  - web
permalink: /network/webserver/session/
---

**Session** 技术是为了解决 **HTTP 协议无状态** 问题而产生的：当用户访问网站时，需要将“用户身份”或“临时数据”跨多个请求进行持久化存储。Session 本质上是一种“**服务器端**保存数据 + 客户端保存一个会话标识（Session ID）”的方案。

<!-- more -->

## 为什么

HTTP 协议是**无状态**的，每个请求都是独立的，服务器无法知道当前请求用户是否和上一个请求是同一个人。为了解决 “记录用户登录状态、购物车信息、个性化偏好” 等需求，<span style="color:rgb(255, 0, 0)">后端</span>引入了 Session：

1. **生成 Session ID**：

当用户第一次访问时，服务器创建一条“会话记录”，将其关联一个唯一的 Session ID（如随机字符串）。

2. **Cookie / URL 传递**：

服务器会通过 Set-Cookie 把 Session ID 发送给客户端，客户端在后续请求中自动附带该 Cookie，以便服务器识别用户。

• 如果不使用 Cookie，也可将 Session ID 放在 URL、隐藏字段等，但最常见的还是 Cookie。

3. **在服务端存储数据**：

Session 的核心在于**服务端**保留了一份映射关系，比如一个 map[sessionID]UserData。根据客户端带回的 Session ID，可以快速查找对应的数据（如登录用户 ID、购物车内容）。

## `session`中间件

在多数现代 Web 框架（如 Gin、Beego、Hertz、Django、Express 等）中，Session 以**中间件**（middleware）的形式注入到请求处理流程中：

**请求开始**：

- Session 中间件会从请求头的 `Cookie` 中解析出 Session ID；如果没有，则创建一个新的 Session ID。
- 同时会去查找服务器端的存储（内存、Redis、数据库等）中是否存在与该 Session ID 关联的数据，如果有则加载到内存中以备本次请求使用。

**业务逻辑处理**：

- 在 Handler 内，可以通过 `session.Get(key)` / `session.Set(key, value)` 等方法读写当前用户的 Session 数据，比如记录用户已登录、添加购物车项等。

 **请求结束**：
    
- Session 中间件将更新后的 Session 写回存储（若有修改），并在响应头中设置/更新 `Cookie: sessionID=...`（若新生成了 Session ID 或变更了其他参数）。

## `session`存储

**内存存储（MemoryStore）**

- 直接存在服务器内存中，查询速度快，但不适合分布式、且内存重启丢失数据。

**文件存储**

- 将 Session 数据写到文件，每个 Session ID 对应一个文件，适合低并发场景。

**Redis / Memcached**

- 分布式场景常用，通过 `SessionID` 作为 key 在 Redis 查找对应哈希或字符串值。可在多台服务器共享 Session 信息。

**Cookie 存储**

- 将 Session 数据本身加密签名后放在客户端 Cookie 中，服务器端无需额外数据库。这被称为“**无服务器端存储的 Session**” (也有称之为 “Cookie Session”)，只要防止被篡改即可。

## `Hertz`的 `Session`实现

```go
package main

import (
    "context"
    "github.com/cloudwego/hertz/pkg/app"
    "github.com/cloudwego/hertz/pkg/app/server"
    // Session相关包
    "github.com/hertz-contrib/sessions"
    "github.com/hertz-contrib/sessions/cookie"
)

func main() {
    h := server.Default()

    // 1. 创建基于Cookie的session存储
    store := cookie.NewStore([]byte("secret-key"))

    // 2. 在Hertz上注册session中间件
    h.Use(sessions.New("hertz-session", store))

    // 3. 在Handler里读写session
    h.GET("/login", func(ctx context.Context, c *app.RequestContext) {
        session := sessions.Default(c)
        // 把用户ID保存进session
        session.Set("user_id", 1001)
        // 必须调用Save()才会真正写回
        session.Save()

        c.String(200, "Session set: user_id=1001")
    })

    h.GET("/profile", func(ctx context.Context, c *app.RequestContext) {
        session := sessions.Default(c)
        userID := session.Get("user_id")
        if userID == nil {
            c.String(401, "Not logged in!")
            return
        }
        c.String(200, "Hello userID=%v", userID)
    })

    h.Spin()
}

```