---
title: Redirecting
createTime: 2024-7-9
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Redirecting.
permalink: /NextJS_AppRouter3/
---
<br> This note records things about Redirecting.
<!-- more -->

## 重定向函数

| API                             | 目的             | 哪里                  | 状态码                 |
| ------------------------------- | -------------- | ------------------- | ------------------- |
| `redirect`                      | 在发生突变或事件后重定向用户 | 服务器组件、服务器操作、路由处理程序  | 307（临时）或 303（服务器操作） |
| `permanentRedirect`             | 在发生突变或事件后重定向用户 | 服务器组件、服务器操作、路由处理程序  | 308 （永久）            |
| `useRouter`                     | 执行客户端导航        | 客户端组件中的事件处理程序       | 不适用                 |
| `redirects` in `next.config.js` | 根据路径重定向传入请求    | `next.config.js` 文件 | 307（临时）或 308（永久）    |
| `NextResponse.redirect`         | 根据条件重定向传入请求    | 中间件                 | 任何                  |

## Redirect

该 `redirect` 函数允许您将用户重定向到另一个 URL。您可以调用 `redirect` 服务器组件、路由处理程序和服务器操作。

`redirect` 通常在突变或事件后使用。例如，创建帖子：

```tsx
'use server'
 
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'
 
export async function createPost(id: string) {
  try {
    // Call database
  } catch (error) {
    // Handle errors
  }
 
  revalidatePath('/posts') // Update cached posts
  redirect(`/post/${id}`) // Navigate to the new post page
}
```

> Tips
+ `edirect` 默认情况下返回 307（临时重定向）状态代码。在服务器操作中使用时，它会返回 303（请参阅其他），该 303 通常用于由于 POST 请求而重定向到成功页面。
+ `redirect` 内部抛出错误，因此应在 `try/catch` 块外部调用它。
+ `redirect` 可以在呈现过程中在客户端组件中调用，但不能在事件处理程序中调用。您可以改用 `useRouter` 钩子。
+ `redirect` 也接受 URL，可用于重定向到外部链接。
+ 如果要在渲染过程之前进行重定向，请使用 `next.config.js` 或中间件。

## PermanentRedirect

`permanentRedirect` 函数允许您将用户永久重定向到另一个 URL。您可以调用 `permanentRedirect` 服务器组件、路由处理程序和服务器操作。
 
`permanentRedirect` 通常在更改实体规范 URL 的突变或事件后使用，例如在用户更改用户名后更新用户的个人资料 URL：

```tsx
'use server'
 
import { permanentRedirect } from 'next/navigation'
import { revalidateTag } from 'next/cache'
 
export async function updateUsername(username: string, formData: FormData) {
  try {
    // Call database
  } catch (error) {
    // Handle errors
  }
 
  revalidateTag('username') // Update all references to the username
  permanentRedirect(`/profile/${username}`) // Navigate to the new user profile
}
```

>Tips:
+ `permanentRedirect` 默认情况下返回 308（永久重定向）状态代码。
+ `permanentRedirect` 也接受 URL，可用于重定向到外部链接。

## `useRouter()` 

如果需要在客户端组件的事件处理程序内进行重定向，则可以使用 `useRouter` 挂钩 `push` 中的方法。例如：

```tsx
'use client'
 
import { useRouter } from 'next/navigation'
 
export default function Page() {
  const router = useRouter()
 
  return (
    <button type="button" onClick={() => router.push('/dashboard')}>
      Dashboard
    </button>
  )
}
```

>Tips:
+ 如果不需要以编程方式导航用户，则应使用 `<Link>` 组件。

## `next.config.js`

`next.config.js` 文件中的 `redirects` 选项允许您将传入请求路径重定向到其他目标路径。当您更改页面的 URL 结构或拥有提前已知的重定向列表时，这很有用。

`redirects` 支持路径、标头、Cookie 和查询匹配，使您可以灵活地根据传入请求重定向用户。

要使用 `redirects` ，请将选项添加到您的 `next.config.js` 文件中：

```js
module.exports = {
  async redirects() {
    return [
      // Basic redirect
      {
        source: '/',
        destination: '/dashboard',
        permanent: true,
	  }
    ]
  },
}
```

> Tips:
+ `redirects` 可以使用该 `permanent` 选项返回 307（临时重定向）或 308（永久重定向）状态代码。
+ `redirects` 可能对平台有限制。例如，在 Vercel 上，重定向限制为 1,024 个。若要管理大量重定向 （1000+），请考虑使用中间件创建自定义解决方案。有关详细信息，请参阅大规模管理重定向。
+ `redirects` 在中间件之前运行。

**warning**
+ 谨慎使用 `permanent`选项，它会使客户端记住该重定向缓存，即使以后再构建时取消了改重定向，记住缓存的客户端仍然会发生重定向事件。

## Redirect In MiddleWare

中间件允许您在请求完成之前运行代码。然后，根据传入的请求，使用 `NextResponse.redirect` .如果要根据条件（例如身份验证、会话管理等）重定向用户或具有大量重定向，这将非常有用。

例如，要将用户重定向到未通过身份验证的 `/login` 页面，请执行以下操作：

```ts
import { NextResponse, NextRequest } from 'next/server'
import { authenticate } from 'auth-provider'
 
export function middleware(request: NextRequest) {
  const isAuthenticated = authenticate(request)
 
  // If the user is authenticated, continue as normal
  if (isAuthenticated) {
    return NextResponse.next()
  }
 
  // Redirect to login page if not authenticated
  return NextResponse.redirect(new URL('/login', request.url))
}
 
export const config = {
  matcher: '/dashboard/:path*',
}
```

>Tips:
+ 中间件在渲染之后 `redirects` `next.config.js` 和渲染之前运行。

## 路由组

在 Next.js 中，`app` 目录中的嵌套文件夹通常映射到 URL 路径。这意味着如果你在 `app` 目录中创建了一个文件夹，该文件夹的名称会成为 URL 的一部分。但是，你可以将文件夹标记为路由组，这样该文件夹的名称就不会包含在 URL 路径中。

这允许您将路由段和项目文件组织到逻辑组中，而不会影响 URL 路径结构

### 约定

可以通过将文件夹的名称括在括号中来创建路由组： `(folderName)`

### 例子

若要在不影响 URL 的情况下组织路由，请创建一个组以将相关路由保持在一起。括号中的文件夹将从 URL 中省略（例如 `(marketing)` 或 `(shop)` ）。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Froute-group-organisation.png&w=1920&q=75)

即使路由内部 `(marketing)` 并 `(shop)` 共享相同的 URL 层次结构，您也可以通过在其文件夹中添加 `layout.js` 文件来为每个组创建不同的布局。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Froute-group-multiple-layouts.png&w=1920&q=75)

### 将特定区段选择到布局中

要选择将特定路由添加到布局中，请创建一个新的路由组（例如 `(shop)` ），并将共享相同布局的路由移动到该组中（例如 `account` 和 `cart` ）。组外的路由不会共享布局 ， 例如 `checkout`

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Froute-group-opt-in-layouts.png&w=1920&q=75)

### 多个根布局

要创建多个根布局，请删除顶级 `layout.js` 文件，然后在每个路由组中添加一个 `layout.js` 文件。这对于将应用程序划分为具有完全不同 UI 或体验的部分非常有用。 `<html>` 需要将 and `<body>` 标记添加到每个根布局中。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Froute-group-multiple-root-layouts.png&w=1920&q=75)
