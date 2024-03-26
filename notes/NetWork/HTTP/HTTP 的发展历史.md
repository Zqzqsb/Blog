---
title: HTTP 的发展历史
createTime: 2024-3-26
author: ZQ
---

## HTTP 0.9

最初版本的 `HTTP` 协议并没有版本号，后来它的版本号被定位在 0.9 以区分后来的版本。

### 请求

```HTTP
GET /mypage.html
```

### 响应

```html
<html>
  这是一个非常简单的 HTML 页面
</html>
```

### 特点

- 只能使用 `GET` ，且一旦连接到服务器，协议、服务器、端口号这些都不是必须的。
- 不含状态码。
- 只能传输 `html` 格式。

## HTTP 1.0

可以参照  [RFC 1945](https://datatracker.ietf.org/doc/html/rfc1945)来核实本文的内容。一个典型的`HTTP 1.0` 请求

```HTTP
GET /mypage.html HTTP/1.0
User-Agent: NCSA_Mosaic/2.0 (Windows 3.1)

200 OK
Date: Tue, 15 Nov 1994 08:12:31 GMT
Server: CERN/3.0 libwww/2.17
Content-Type: text/html
<HTML>
一个包含图片的页面
  <IMG SRC="/myimage.gif">
</HTML>
```

- `GET POST HEAD` 请求方法
- 引入了状态码
- 引入了`HTTP`标头用于传输元数据
- 借助 `Content-Type` 字段传输其他文档类型
- 映入了缓存控制控制字段
  - IF-Modified-Since : The If-Modified-Since request-header field is used with the GET method to make it conditional: if the requested resource has not been modified since the time specified in this field, a copy of the resource will not be returned from the server; instead, a 304 (**not modified , redirect to local cache**).response will be returned without any Entity-Body. (**用于支持协商缓存**)
  - Last-Modified : The Last-Modified entity-header field indicates the date and time at which the sender believes the resource was last modified. (**用于支持强缓存**)
  - Program: no-cache(**不使用强缓存**)

## HTTP 1.1

发布在`HTTP1.0`的下一年，修订并消除了诸多歧义。也是目前最流行的`HTTP` 版本。最近一次修订的相关文档[RFC 7235](https://datatracker.ietf.org/doc/html/rfc7235)。

### 一个典型的 HTTP 连接

```HTTP
GET /static/img/header-background.png HTTP/1.1
Host: developer.mozilla.org
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://developer.mozilla.org/zh-CN/docs/Glossary/Simple_header

200 OK
Age: 9578461
Cache-Control: public, max-age=315360000
Connection: keep-alive
Content-Length: 3077
Content-Type: image/png
Date: Thu, 31 Mar 2016 13:34:46 GMT
Last-Modified: Wed, 21 Oct 2015 18:27:50 GMT
Server: Apache

(image content of 3077 bytes)
****
```

### 引入新特性

- TCP 复用 ，管线化
  - 引入了管道机制,即在同一个`TCP`连接中，客户端可以**同时**发送多个请求。或者说，允许在第一个应答被完全发送之前就发送第二个请求，以降低通信延迟。
- 支持响应分块
- 范围请求
  - 对应状态码` 206(Partial Content)` 用于支持断点续传
- 额外的缓存控制机制。
  - `Cache-control` : 用于指定缓存策略
  - `Etag / IF-None-Match` 用于执行`cache`效验
  - 相比基于过期时间的效验，`Etag`效验没有时间戳不一致的问题，但同时对服务器的运算能力提出更高的要求
- 内容协商机制
  - 包括语言、编码、类型等。并允许客户端和服务器之间约定以最合适的内容进行交换。
- 凭借  `Host` 标头
  - `HTTP1.0`中认为每台服务器都绑定一个唯一的 IP 地址，因此，请求消息中的 URL 并没有传递主机名（`hostname`）。但随着虚拟主机技术的发展，在一台物理服务器上可以存在多个虚拟主机（`Multi-homed Web Servers`），并且它们共享一个 IP 地址。`HTTP1.1`的请求消息和响应消息都应支持`Host`头域，且请求消息中如果没有 Host 头域会报告一个错误（`400 Bad Request`）。有了`Host`字段，就可以将请求发往同一台服务器上的不同网站，为虚拟主机的兴起打下了基础。
- 持久连接
  - HTTP/1.1 最大的变化就是引入了持久连接（persistent connection），在 HTTP/1.1 中默认开启  `Connection: keep-alive`，即 TCP 连接默认不关闭，可以被多个请求复用。

### 缺点

**对头阻塞**
HTTP/1.1 的持久连接和管道机制允许复用 TCP 连接，在一个 TCP 连接中，也可以同时发送多个请求，但是所有的数据通信都是按次序完成的，服务器只有处理完一个回应，才会处理下一个回应。比如客户端需要 A、B 两个资源，管道机制允许浏览器同时发出 A 请求和 B 请求，但服务器还是按照顺序，先回应 A 请求，完成后再回应 B 请求，这样如果前面的回应特别慢，后面就会有很多请求排队等着，这称为“队头阻塞（Head-of-line blocking）”

## HTTP 2.0

## HTTP 3.0
