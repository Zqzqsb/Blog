---
title: Dynamic Route
createTime: 2024-7-10
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Dynamic Route.
---
<br> This note records things about Dynamic Route.
<!-- more -->
## 动态路由概述

如果您事先不知道确切的区段名称并希望从动态数据创建路由，则可以使用在请求时填充或在构建时预呈现的动态区段。

## 约定

可以通过将文件夹的名称括在方括号中来创建动态区段： `[folderName]` 。例如， `[id]` 或 `[slug]`。

动态段作为 `params` 、 `page` 、 `route` 和 `generateMetadata` 函数的道具 `layout` 传递。

## 例子

例如，博客可以包含以下路线 `app/blog/[slug]/page.js` ，其中 `[slug]` 是博客文章的动态段。

```tsx
export default function Page({ params }: { params: { slug: string } }) {
  return <div>My Post: {params.slug}</div>
}
```

```shell
➜  blog git:(main) ✗ tree 
.
└── [slug]
    ├── a.tsx
    └── page.tsx

2 directories, 2 files
```

访问 `/blog/a`时，会动态路由到`a.tsx`对应渲染内容。

### 生成静态路由参数

该 `generateStaticParams` 函数可以与动态路段结合使用，以在构建时静态生成路由，而不是在请求时按需生成路由。

```tsx
export async function generateStaticParams() {
  const posts = await fetch('https://.../posts').then((res) => res.json())
 
  return posts.map((post) => ({
    slug: post.slug,
  }))
}
```

该 `generateStaticParams` 功能的主要优点是可以智能检索数据。如果使用 `fetch` 请求在 `generateStaticParams` 函数中获取内容，则会自动记住请求。这意味着在多个 `generateStaticParams` 、布局和页面上具有相同参数 `fetch` 的请求将只发出一次，从而缩短构建时间。

### Catch-all

动态段可以通过在括号内添加省略号来扩展为捕获所有后续段 `[...folderName]` 。

例如， `app/shop/[...slug]/page.js` 将匹配 ，但也 `/shop/clothes/tops` 匹配 `/shop/clothes` 、 `/shop/clothes/tops/t-shirts` 等。

| Route 路线                     | Example URL 示例 URL | `params`                    |
| ---------------------------- | ------------------ | --------------------------- |
| `app/shop/[...slug]/page.js` | `/shop/a`          | `{ slug: ['a'] }`           |
| `app/shop/[...slug]/page.js` | `/shop/a/b`        | `{ slug: ['a', 'b'] }`      |
| `app/shop/[...slug]/page.js` | `/shop/a/b/c`      | `{ slug: ['a', 'b', 'c'] }` |
### Optional Catch-all

通过在双方括号中包含参数，可以使 Catch-all Segments 成为可选的： `[[...folderName]]` 。

例如， `app/shop/[[...slug]]/page.js` 还会匹配 `/shop` ，除了 `/shop/clothes` 、 `/shop/clothes/tops` 。 `/shop/clothes/tops/t-shirts`

| oute 路线                        | Example URL 示例 URL | `params`                    |
| ------------------------------ | ------------------ | --------------------------- |
| `app/shop/[[...slug]]/page.js` | `/shop`            | `{}`                        |
| `app/shop/[[...slug]]/page.js` | `/shop/a`          | `{ slug: ['a'] }`           |
| `app/shop/[[...slug]]/page.js` | `/shop/a/b`        | `{ slug: ['a', 'b'] }`      |
| `app/shop/[[...slug]]/page.js` | `/shop/a/b/c`      | `{ slug: ['a', 'b', 'c'] }` |
catch-all 和 optional catch-all 段之间的区别在于，使用 optional，不带参数的路由也会匹配（在上面的示例 `/shop` 中）。
