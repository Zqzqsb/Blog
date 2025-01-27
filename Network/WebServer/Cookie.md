---
title: Cookie
createTime: 2025-1-27
author: ZQ
tags:
  - web
permalink: /network/webserver/cookie/
---

**Cookie 是 HTTP 协议层面（准确说是 HTTP 的扩展/附属标准）的一种状态管理机制**

<!-- more --> 

## 起源

在最初的 HTTP 协议版本中，HTTP 本身是无状态的，为了让服务端和客户端能够记住一些用户状态（如登录状态、偏好设置、购物车信息等），就引入了 Cookie 这一机制。Cookie 的规范最早由 Netscape 提出，随后在 IETF 出台的 RFC（如 [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265)）中进行标准化，成为**HTTP 协议中通用的状态管理方式**。

因此，Cookie 从设计和使用上来讲，隶属于 **应用层/HTTP 协议层** 的范畴。浏览器（或其他 HTTP 客户端）在收发 HTTP 请求/响应时会自动处理 Cookie，包括设置、携带和管理 Cookie。服务器端也在 HTTP 响应头中通过 Set-Cookie 字段来下发 Cookie。

## 基本工作原理

• 服务器端在响应头中通过 Set-Cookie 设置 Cookie；
• 客户端（浏览器）收到后会保存下来，并在后续请求的请求头中携带 Cookie: ...，从而实现跨请求的状态维持。

### `cookie`的发送

在**标准的浏览器环境**下，Cookie 的设置与传递通常是**自动**完成的，**不需要**你在前端代码里显式“手动”去存储或发送。

服务器端只需要在 HTTP 响应头里加上 Set-Cookie，浏览器便会自动接收到并存储 Cookie。例如在 Go 里，可能会写：

```go
c.SetHeader("Set-Cookie", "sessionID=abc123; Path=/; HttpOnly")
```

或者调用`HTTP`框架中的内置方法

```go
c.SetCookie("sessionID", "abc123", 3600, "/", "example.com", false, true)
```

当浏览器收到带有 Set-Cookie 的响应时，它会自动将这个 Cookie 存储到浏览器内部的“Cookie 存储”中，无需前端手动处理。

### `cookie`的携带

1. **浏览器自动发送**

在同源请求的默认场景里，浏览器会在后续对相同域名的请求中**自动**带上之前保存的 Cookie。这个过程也不需要手动编写任何前端代码。

2. **跨域请求**

• 如果是使用 fetch 或 axios 等库去**跨域**请求，默认情况下并不会发送 Cookie。需要在请求配置里显式开启“跨域允许携带 Cookie”。例如：

```js
fetch("https://api.example.com/data", {
  method: "GET",
  credentials: "include" // 关键点
});
```

同时服务器也需要设置 Access-Control-Allow-Credentials 等响应头，才能使浏览器允许跨域携带并接收 Cookie。

## `cookie`的内容

**1. 客户端的 HTTP 请求示例**

一般在浏览器或 HTTP 客户端发出请求时，如果之前服务器下发过 Cookie，并且还在有效期内，浏览器会在请求头里自动附加 Cookie 字段。例如：

```http
GET /profile HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
Accept: text/html,application/xhtml+xml,application/xml
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Cookie: sessionID=abc123; theme=dark; userID=42
```

• **sessionID=abc123**：典型的 Session 标识，用来让服务器识别当前用户的会话。
• **theme=dark**：用户界面偏好，比如深色模式。
• **userID=42**：有些网站也会把用户 ID 存在 Cookie 里（不过更安全的做法是存 Session 里或使用 Token）。

**2. 服务器端的 HTTP 响应示例**

服务器在需要设置或更新 Cookie 时，会在响应头中返回 Set-Cookie。例如：

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Set-Cookie: sessionID=abc123; Path=/; Max-Age=3600; HttpOnly; Secure
Set-Cookie: theme=dark; Path=/; Expires=Wed, 15 Feb 2025 10:00:00 GMT
Content-Length: 4523
Date: Thu, 30 Jan 2025 09:58:29 GMT

<!DOCTYPE html>
<html>
<head> ... </head>
<body> ... </body>
</html>
```

1. **sessionID=abc123**

• Path=/：表示此 Cookie 在整个网站（以“/”开头的所有路径）下都有效。
• Max-Age=3600：表示此 Cookie 在**浏览器端**存活 3600 秒（1 小时）。到期后，浏览器将自动删除该 Cookie。
• HttpOnly：禁止 JavaScript 读取该 Cookie，可防止大多数 XSS 攻击窃取 Cookie。
• Secure：只有在 HTTPS 连接时才会传递该 Cookie，防止明文传输。

2. **theme=dark**
3. 
• Expires=Wed, 15 Feb 2025 10:00:00 GMT：指定一个绝对过期时间（GMT 格式的日期）。超过这个时间点，浏览器即删除该 Cookie。
• Path=/：同上，Cookie 适用于网站所有路径。

注意：在实际使用中，过期策略要么指定 Max-Age（相对时间），要么指定 Expires（绝对时间），二者都可以控制 Cookie 的失效。

## 服务端处理逻辑

1. **解析与验证**

• 服务器接收到请求时，会在请求头中找到 Cookie: ...，然后解析其中的 key=value 对（如 sessionID=abc123）。
• 通过这个 sessionID，服务器可在后端存储（内存、数据库、Redis 等）里查找对应的用户会话数据。
• 如果找到匹配记录，就说明用户处于登录状态或已有会话上下文；如果找不到或已过期，则视为“未登录”或“无会话”。

2. **更新或清除 Cookie**

• 在某些场景（如用户刚登录成功），服务器需要告诉客户端“新的 sessionID”，就会返回一个 Set-Cookie 头；若需要清除 Cookie，可以设置过期时间为过去的日期或 Max-Age=0 来使其失效。

3. **存储位置**

• **Cookie 本身**最主要是存在**客户端（浏览器）**里。服务器只保存与之对应的会话数据（如果使用 Session），或验证 Token（如果使用 JWT）。
• 对于基于**Session**的场景：sessionID 就是把会话数据存放在服务器端（如 Redis、内存、数据库），只在客户端保存一个“Session ID”来关联服务器上的数据。
• 对于**无状态**的场景（例如 JWT）：Set-Cookie 里可能直接放 token=xxxxx，服务器只要验证该 Token 的签名和有效期即可，而无需额外存储会话。

4. **过期策略**

• 服务器设置 Expires 或 Max-Age 告诉客户端何时删除 Cookie。
• 如果使用 Session 机制，服务器端也会设置会话的过期时间（比如 session 过期 30 分钟），届时即使客户端还带着 Cookie，但服务端已清除或者不再认可该 sessionID，也会视为无效。

**4. Cookie 的几个常见属性及作用**

1. Expires **/** Max-Age：控制 Cookie 的**失效时间**。
2. Path：指定 Cookie 对应的路径范围，只有请求路径匹配才会发送此 Cookie。
3. Domain：指定 Cookie 对应的域名范围，只有请求的域与该配置匹配才会发送。
4. HttpOnly：启用后，客户端 JavaScript 无法读取此 Cookie，提升安全性。
5. Secure：启用后仅在 HTTPS 连接时发送，防止敏感信息明文泄露。
6. SameSite：控制跨站请求携带 Cookie 的策略，可减少 CSRF 风险。典型值：Strict、Lax、None。