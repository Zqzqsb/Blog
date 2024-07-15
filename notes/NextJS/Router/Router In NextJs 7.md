---
title: Routes Handlers
createTime: 2024-7-13
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Routes Handlers.
---
<br> This note records things about Routes Handlers.
<!-- more -->

## 概述

路由处理程序允许您使用 Web 请求和响应 API 为给定路由创建自定义请求处理程序。

>Tips:
+ 路由处理程序仅在 `app` 目录中可用。它们相当于 `pages` 目录中的 API 路由，这意味着您不需要同时使用 API 路由和路由处理程序。

## 约定

路由处理程序在 `app` 目录内的 `route.js|ts` 文件中定义：

```tsx
export const dynamic = 'force-dynamic' // defaults to auto
export async function GET(request: Request) {}
```

路由处理程序可以嵌套在 `app` 目录中，类似于 `page.js` 和 `layout.js` 。但在与 `page.js` 相同的路线段级别上不能存在 `route.js` 文件。

### HTTP Method

支持以下 HTTP 方法： `GET` 、 `POST` 、 `PUT` 、 `PATCH` 、 `DELETE` 、 `HEAD` 和 `OPTIONS` 。如果调用不受支持的方法，Next.js 将返回 `405 Method Not Allowed` 响应。

## Behavior

### caching

当将 `GET` 方法与 `Response` 对象一起使用时，默认情况下会缓存路由处理程序。

```tsx
export async function GET() {
  const res = await fetch('https://data.mongodb-api.com/...', {
    headers: {
      'Content-Type': 'application/json',
      'API-Key': process.env.DATA_API_KEY,
    },
  })
  const data = await res.json()
 
  return Response.json({ data })
}
```
### 取消缓存

+ 将 `Request` 对象与 `GET` 方法一起使用。
+ 使用任何其他 HTTP 方法。
+ 使用动态函数，例如 `cookies` 和 `headers` 。
+ 段配置选项手动指定动态模式。
