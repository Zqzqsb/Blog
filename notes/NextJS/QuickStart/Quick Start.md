---
title: Quick Start
createTime: 2024-7-8
author: ZQ
tags:
  - react
  - NextJs
description: NextJS 快速入门
---
<br> NextJS 快速入门
<!-- more -->

## `Next.js` 文件结构

在 Next.js 中，有几个约定俗成的文件和目录：

- **`pages/` 目录**：用于定义页面组件，每个文件对应一个路由。
- **`app/` 目录**（Next.js 13 引入的实验性功能）：用于定义更灵活的布局和路由。

```shell
➜  app git:(main) ✗ tree
.
├── layout.tsx
└── page.tsx
1 directory, 2 files
```

### `layout.tsx` 和 `page.tsx` 的作用

- **`layout.tsx`**：通常用于定义应用的布局结构，比如导航栏、侧边栏和页脚等。这个文件中的内容**会包裹每一个页面**。
- **`page.tsx`**：定义具体的页面内容，每个文件对应一个特定的路由。

### 自动解析和传递

`Next.js` 会自动解析 `layout.tsx` 和 `page.tsx`，并将 `page.tsx` 作为子组件传递给 `layout.tsx` 中定义的布局。

## `APP Route`

`App Router` 使用 `app/` 目录来组织路由和布局。在这个目录中，每个子目录和文件都可以代表一个路由。

```shell
my-next-app/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── about/
│   │   └── page.tsx
│   └── contact/
│       └── page.tsx
├── public/
├── styles/
├── package.json
└── next.config.js

```

- `app/`: 这是根目录，包含所有路由和布局。
- `layout.tsx`: 定义全局布局，应用于所有页面。
- `page.tsx`: 定义根路径 `/` 的页面。
- `about/page.tsx`: 定义 `/about` 路径的页面。
- `contact/page.tsx`: 定义 `/contact` 路径的页面。

## APP 目录

创建一个 `app/` 文件夹，然后添加一个 `layout.tsx` and `page.tsx` 文件。当用户访问应用程序的根目录 （ `/` ） 时，将呈现这些内容。

在 `app/layout.tsx` 里面创建一个带有必需 `<html>` 和 `<body>` 标签的根布局：

```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

这个布局页面会将传入任何元素做简单包裹。

`React.ReactNode` 是 React 中的一个类型，表示可以被渲染的任意内容，包括元素、字符串、数字、片段等。

在`page.tsx`中写一些内容，就能启动一个最简单的应用。

```tsx
export default function Page() {
	return <h1>Hello, Next.js!</h1>
}
```
