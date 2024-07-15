---
title: Parallel Routes
createTime: 2024-7-10
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Parallel Routes.
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


### `useSelectedLayoutSegments`

`useSelectedLayoutSegment` 和 `useSelectedLayoutSegments` 都接受 `parallelRoutesKey` 参数，该参数允许您读取槽内的活动路线段。

```tsx
'use client'
 
import { useSelectedLayoutSegment } from 'next/navigation'
 
export default function Layout({ auth }: { auth: React.ReactNode }) {
  const loginSegment = useSelectedLayoutSegment('auth')
  // ...
}
```

当用户导航到 `app/@auth/login` （或 URL 栏中的 `/login` ）时， `loginSegment` 将等于字符串 `"login"` 。

**`const loginSegment = useSelectedLayoutSegment('auth')`**:

- 使用 `useSelectedLayoutSegment` 钩子获取名为 `auth` 的插槽的当前活动路由段，并将其存储在 `loginSegment` 变量中。

## 使用场景

### 条件路由

您可以使用并行路由根据某些条件（例如用户角色）有条件地渲染路由。例如，要为 `/admin` 或 `/user` 角色呈现不同的仪表板页面

```tsx
import { checkUserRole } from '@/lib/auth'
 
export default function Layout({
  user,
  admin,
}: {
  user: React.ReactNode
  admin: React.ReactNode
}) {
  const role = checkUserRole()
  return <>{role === 'admin' ? admin : user}</>
}
```

### 选项组

您可以在槽内添加 `layout` 以允许用户独立导航该槽。这对于创建选项卡很有用。

例如， `@analytics` 插槽有两个子页面： `/page-views` 和 `/visitors` 。

在 `@analytics` 中，创建一个 `layout` 文件以在两个页面之间共享选项卡：

```tsx
import Link from 'next/link'
 
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <nav>
        <Link href="/page-views">Page Views</Link>
        <Link href="/visitors">Visitors</Link>
      </nav>
      <div>{children}</div>
    </>
  )
}
```

### Modals

并行路由可以与拦截路由一起使用来创建模态。这使您可以解决构建模式时的常见挑战，例如：

+ 使模态内容可通过 URL 共享。
+ 刷新页面时保留上下文，而不是关闭模式。
+ 关闭向后导航的模式，而不是转到上一个路线。
+ 重新打开向前导航的模式。

考虑以下 UI 模式，用户可以使用客户端导航从布局打开登录模式，或访问单独的 `/login` 页面：

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fparallel-routes-auth-modal.png&w=1920&q=75)

要实现此模式，首先创建一个用于呈现主登录页面的 `/login` 路由。

```tsx
import { Login } from '@/app/ui/login'
 
export default function Page() {
  return <Login />
}
```

然后，在 `@auth` 槽内添加返回 `null` 的 `default.js` 文件。这可确保模态在不活动时不会呈现。

```tsx
export default function Default() {
  return null
}
```

在您的 `@auth` 插槽中，通过更新 `/(.)login` 文件夹来拦截 `/login` 路由。将 `<Modal>` 组件及其子组件导入到 `/(.)login/page.tsx` 文件中：

```tsx
import { Modal } from '@/app/ui/modal'
import { Login } from '@/app/ui/login'
 
export default function Page() {
  return (
    <Modal>
      <Login />
    </Modal>
  )
}
```

## 拦截路由

拦截路由允许您从当前布局内应用程序的其他部分加载路由。当您想要显示路由内容而不需要用户切换到不同的上下文时，此路由范例非常有用。

例如，当单击源中的照片时，您可以在模式中显示照片，覆盖源。在这种情况下，Next.js 拦截 `/photo/123` 路由，屏蔽 URL，并将其覆盖在 `/feed` 上。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fintercepting-routes-soft-navigate.png&w=1920&q=75)

但是，当通过单击可共享 URL 或刷新页面导航到照片时，应呈现整个照片页面而不是模式。不应发生路由拦截。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fintercepting-routes-hard-navigate.png&w=1920&q=75)

拦截路由可以使用 `(..)` 约定来定义，它类似于相对路径约定 `../` ，但针对的是段。

You can use: 您可以使用：

- `(.)` to match segments on the **same level**  
- `(..)` to match segments **one level above**  
- `(..)(..)` to match segments **two levels above**  
- `(...)` to match segments from the **root** `app` directory  

例如，您可以通过创建 `(..)photo` 目录从 `feed` 段中拦截 `photo` 段。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fintercepted-routes-files.png&w=1920&q=75)

### 例子

考虑以下 UI 模式，用户可以使用客户端导航从图库中打开照片模式，或直接从可共享 URL 导航到照片页面：

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fintercepted-routes-modal-example.png&w=1920&q=75)

在上面的示例中， `photo` 段的路径可以使用 `(..)` 匹配器，因为 `@modal` 是一个槽而不是一个段。这意味着 `photo` 路由仅高一级段，尽管文件系统级别高两级。
