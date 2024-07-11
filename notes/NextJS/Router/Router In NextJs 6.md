---
title: Parallel Routes
createTime: 2024-7-10
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Parallel Routes.
permalink: /NextJS_AppRouter6/
---
<br> This note records things about Parallel Routes.
<!-- more -->
##  Parallel Routes 概述

“并行路由”允许您在同一布局中同时或有条件地呈现一个或多个页面。它们对于应用的高度动态部分非常有用，例如社交网站上的仪表板和源。

例如，考虑仪表板，您可以使用并行路由同时呈现 `team` 和 `analytics` 页面：

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fparallel-routes.png&w=1920&q=75)

```tsx
➜  parallelRoutes git:(0ab53bc) tree
.
├── @analytics
│   └── page.tsx
├── layout.tsx
├── page.tsx
└── @team
    └── page.tsx

3 directories, 4 files
```

`app-router`对应的位置添加了平行路由demo，效果如图。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/NextJS/ParallelRoute.png)

## Slots

使用命名时隙创建并行路由。插槽是按照 `@folder` 约定定义的。例如，以下文件结构定义了两个插槽： `@analytics` 和 `@team` ：

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fparallel-routes-file-system.png&w=1920&q=75)

插槽作为道具传递到共享父布局。对于上面的例子，组件 `app/layout.js` 现在接受 `@analytics` 和 `@team` slot 道具，并且可以与 `children` prop 并行渲染它们:

```tsx
export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <>
      {children}
      {team}
      {analytics}
    </>
  )
}
```

但是，插槽不是路由段，不会影响 URL 结构。例如，对于 `/@analytics/views` ，URL 将是 `/views` 因为 `@analytics` 是一个插槽。

>Tips:
+ `children` prop 是一个不需要映射到文件夹的隐式插槽。此均值 `app/page.js` 等价于 `app/@children/page.js` 。

## 活动状态和导航

默认情况下，Next.js 会跟踪每个插槽的活动状态（或子页面）。但是，在插槽中呈现的内容将取决于导航类型：

**软导航（Soft Navigation）**：

- 在软导航期间，例如从一个页面导航到另一个页面但不进行整页刷新时，Next.js会执行部分渲染。它会更新当前页面的某些部分（或插槽），例如替换主要内容区域的子页面，同时保留其他部分不变，即使它们与当前URL不匹配。
- 这种方式使得用户在导航时可以享受到更快的响应速度，因为页面不需要完全重新加载，只需更新必要的部分。

**硬导航（Hard Navigation）**：

- 硬导航通常发生在整页加载时，例如用户进行浏览器刷新或直接访问某个URL时。在这种情况下，Next.js不会记住不匹配当前URL的插槽的状态。
- 如果某些插槽在硬导航后没有与新URL匹配的内容，Next.js会尝试渲染一个默认的文件（例如default.js），或者如果未提供默认文件，则可能会渲染一个404页面。
- 这种行为确保了页面的正确性和可靠性，尽管在硬导航时可能会带来一些加载时间上的延迟和全局刷新。

> Tips:
+ `404` 对于不匹配的路由有助于确保您不会意外地在页面上呈现并行路由。

### `default.js`

您可以定义一个 `default.js` 文件，作为初始加载或整页重新加载期间不匹配插槽的回退。

请考虑以下文件夹结构。 `@team` 插槽有一个 `/settings` 页面，但 `@analytics`没有。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fparallel-routes-unmatched-routes.png&w=1920&q=75)

导航到 `/settings` 时， `@team` 插槽将呈现 `/settings` 页面，同时维护 `@analytics` 插槽的当前活动页面。

刷新时 `Next.js` 将为 `@analytics` 渲染 `default.js` 。如果 `default.js` 不存在，则会渲染 `404` 。

此外，由于 `children` 是一个隐式插槽，因此您还需要创建一个 `default.js` 文件， `children` 以便在`Next.js`无法恢复父页面的活动状态时呈现回退。
