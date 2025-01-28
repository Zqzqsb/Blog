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