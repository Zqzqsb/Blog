---
title: LearnJS APP Route 1
createTime: 2024-7-8
author: ZQ
tags:
  - react
  - NextJs
description: NextJS App Router
permalink: /NextJS_AppRouter/
---
<br> NextJS App Router
<!-- more -->

## 本篇笔记的结构

+ 文件定义路由
+ Page, layout 和 Template
+ 不同时机的重定向
+ 路由和导航的工作原理

## 文件定义路由

Next.js使用基于文件系统的路由器，其中文件夹用于定义路由。
每个文件夹表示映射到 URL 段的路由段。若要创建嵌套路由，可以将文件夹嵌套在彼此内部。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Froute-segments-to-path-segments.png&w=1920&q=75)

`page.js` 文件用于使路由段可公开访问。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fdefining-routes.png&w=1920&q=75)

在此示例中， `/dashboard/analytics` URL 路径不可公开访问，因为它没有相应的 `page.js` 文件。此文件夹可用于存储组件、样式表、图像或其他共置文件。

在`dashboard`的`page.js`中添加内容，便能在对应的路由中查看渲染后的内容。

```tsx
// `app/dashboard/page.tsx` is the UI for the `/dashboard` URL
export default function Page() {
  return <h1>Hello, Dashboard Page!</h1>
}
```

> Tips:
- The `.js`, `.jsx`, or `.tsx` file extensions can be used for Pages.  
- A page is always the [leaf](https://nextjs.org/docs/app/building-your-application/routing#terminology) of the [route subtree](https://nextjs.org/docs/app/building-your-application/routing#terminology).  
- A `page.js` file is required to make a route segment publicly accessible.  
- Pages are [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components) by default, but can be set to a [Client Component](https://nextjs.org/docs/app/building-your-application/rendering/client-components).  

## Layout

+ 布局是在多个路由之间共享的 UI。在导航时，布局会保留状态，保持交互式，并且不会重新渲染。布局也可以嵌套。
+ 默认情况下，文件夹层次结构中的布局是嵌套的，这意味着它们通过其 `children` prop 包装子布局。您可以通过在特定路段（文件夹）内添加 `layout.js` 来嵌套布局。
+ 例如，若要为 `/dashboard` 路由创建布局，请在 `dashboard` 文件夹中添加一个新 `layout.js` 文件：
	![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fnested-layout.png&w=1920&q=75)
	![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fnested-layouts-ui.png&w=1920&q=75)

+ 如图所示，在使用布局时，根布局将包裹仪表盘布局。

> Tips:
- `.js`, `.jsx`, or `.tsx` file extensions can be used for Layouts.  
- Only the root layout can contain `<html>` and `<body>` tags.  
- When a `layout.js` and `page.js` file are defined in the same folder, the layout will wrap the page.  
- Layouts are [Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components) by default but can be set to a [Client Component](https://nextjs.org/docs/app/building-your-application/rendering/client-components).  
- Layouts can fetch data. View the [Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching) section for more information.  
- Passing data between a parent layout and its children is not possible. However, you can fetch the same data in a route more than once, and React will [automatically dedupe the requests](https://nextjs.org/docs/app/building-your-application/caching#request-memoization) without affecting performance.  
- Layouts do not have access to the route segments below itself. To access all route segments, you can use [`useSelectedLayoutSegment`](https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segment) or [`useSelectedLayoutSegments`](https://nextjs.org/docs/app/api-reference/functions/use-selected-layout-segments) in a Client Component.  
- You can use [Route Groups](https://nextjs.org/docs/app/building-your-application/routing/route-groups) to opt specific route segments in and out of shared layouts.  
- You can use [Route Groups](https://nextjs.org/docs/app/building-your-application/routing/route-groups) to create multiple root layouts. See an [example here](https://nextjs.org/docs/app/building-your-application/routing/route-groups#creating-multiple-root-layouts).  

## Templates

+ 模板与布局类似，因为它们包装每个子布局或页面。与跨路由保留并维护状态的布局不同，模板在导航时为其每个子项创建一个新实例。这意味着，当用户在共享模板的路由之间导航时，将挂载组件的新实例，重新创建 DOM 元素，不保留状态，并重新同步效果。
+ 在某些情况下，您可能需要这些特定行为，而模板将是比布局更合适的选择。例如：
	+ 依赖于 `useEffect` （例如记录页面浏览量）和 `useState` （例如每页反馈表）的功能。
	+ 更改默认框架行为。例如，布局中的“悬念边界”仅在首次加载布局时显示回退，而在切换页面时不显示回退。对于模板，回退将显示在每个导航上。
	+ 可以通过从 `template.js` 文件中导出默认的 React 组件来定义模板。组件应接受 `children` prop。布局时显示回退，而在切换页面时不显示回退。对于模板，回退将显示在每个导航上。
	
		![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Ftemplate-special-file.png&w=1920&q=75)
	+ `page.js`会被包裹在同级的`template`中，再包裹在`layout`中。

## Link

在主页中插入`link`

```tsx
import Link from 'next/link'

export default function Page() {
return 
	<div>
	## 链接到其他路由
	<Link href="/dashboard" className="outlined text-orange-400">Dashboard</Link>	
	<strong className="text-violet-500"> This is homepage.</strong>
	</div>
}
```

添加一些条件来判断跳转状态，如果当前不在`dashboard`则跳转。

```jsx
"use client";
import Link from "next/link";
import { postcss } from "tailwindcss";
import { usePathname } from "next/navigation";

export default function Page() {
  const pathname = usePathname();
  return (
    <div>
      <Link
        href="/dashboard"
        className={`link ${
          pathname === "/dashboard" ? "text-green-400" : "text-gray-300"
        }`}
      >
        Dashboard
      </Link>
      <strong className="text-violet-500">This is homepage.</strong>
    </div>
  );
}
```

滚动到当期页面的某个部分。

## `useRouter()`钩子

+  `useRouter` 允许您以编程方式从客户端组件更改路由。

```js
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

> Recommendation: Use the `<Link>` component to navigate between routes unless you have a specific requirement for using `useRouter`.

## `useRouter()`  vs `Link`

在 Next.js 中，`useRouter` 和 `Link` 都可以用于路由跳转，但它们在使用方式和适用场景上有所不同。下面是详细的对比：

### **`useRouter()`**

`useRouter` 是一个 React hook，提供了对 Next.js 路由对象的访问。它允许你在函数组件中以编程方式进行导航.
#### 适用场景

- **编程导航**：当你需要在事件处理函数中进行导航（例如按钮点击、表单提交后导航等），使用 `useRouter` 更加灵活。
- **动态路径**：可以根据逻辑动态生成路径并进行导航。
- **访问路由对象**：可以访问路由对象的其他属性和方法，例如 `pathname`、`query` 等。

### **`Link`**

`Link` 是一个组件，专门用于在 Next.js 中创建导航链接。它使用 `<a>` 标签来渲染，提供了客户端路由，无需重新加载页面。
#### 适用场景

- **静态导航**：当你只需要创建一个导航链接时，使用 `Link` 更加简洁。
- **SEO 友好**：`Link` 渲染为 `<a>` 标签，有助于搜索引擎优化。
- **样式和属性传递**：可以直接使用 `<a>` 标签的所有属性和样式。
### 对比总结

- **使用场景**：
    - `useRouter`：适用于需要以编程方式进行导航的场景。
    - `Link`：适用于需要创建静态导航链接的场景。
- **灵活性**：
    - `useRouter`：提供更多灵活性，可以根据逻辑动态生成路径。
    - `Link`：更简洁直观，适合简单的导航需求。
- **SEO 和语义化**：
    - `Link`：渲染为 `<a>` 标签，有助于 SEO 和语义化。
    - `useRouter`：通常用于非链接的导航场景，不直接影响 SEO。
- **代码简洁度**：
    - `Link`：代码更加简洁，适合在 JSX 中直接使用。
    - `useRouter`：需要编写事件处理函数，代码稍微复杂一些。

## Redirect 函数

+ 对于“服务器组件”，改用该 `redirect` 函数

```jsx
import { redirect } from 'next/navigation'
 
async function fetchTeam(id: string) {
  const res = await fetch('https://...')
  if (!res.ok) return undefined
  return res.json()
}
 
export default async function Profile({ params }: { params: { id: string } }) {
  const team = await fetchTeam(params.id)
  if (!team) {
    redirect('/login')
  }
  // ...
}
```

> Tips:
- `redirect` 默认情况下返回 307（临时重定向）状态代码。在服务器操作中使用时，它会返回 303（请参阅其他），该 303 通常用于由于 POST 请求而重定向到成功页面。
- `redirect` 可能在内部报错，因此应在 `try/catch` 块外部调用它。
- 在组件渲染时立即进行重定向，可以使用 `redirect` ；在用户交互事件中进行重定向，需要使用 `useRouter` 钩子。
- `redirect` 也接受 URL，可用于重定向到外部链接。
- 如果要在渲染过程之前进行重定向，请使用 `next.config.js` 或中间件。

## 三种重定向

以上三种重定向方法（渲染前重定向、渲染时重定向和交互事件中重定向）在本质上都是为了将用户从一个路径重定向到另一个路径，但它们在执行时机、应用场景和技术实现上有所不同。下面是对这三种重定向的详细比较和解释：
### 渲染前重定向

**执行时机**: 在服务器接收到请求但在渲染页面之前进行重定向。
**应用场景**: 适用于需要在用户看到页面内容之前进行重定向的情况，例如：
- 基于路径的静态重定向（如重定向旧的 URL 到新的 URL）。
- 基于用户身份验证状态的重定向。
**技术实现**:
- `next.config.js` 的 `redirects` 方法：定义静态重定向规则。
- Middleware：运行自定义逻辑，决定是否重定向。

### 渲染时重定向

**执行时机**: 在客户端组件渲染期间进行重定向。
**应用场景**: 适用于需要在客户端组件渲染时根据某些条件进行重定向的情况，例如：
- 用户在未登录状态下访问某些页面时重定向到登录页面。
- 在组件加载后根据业务逻辑进行重定向。
**技术实现**:
- 使用 `useRouter` 钩子和 `useEffect` 进行重定向。

### 交互事件中重定向

**执行时机**: 在用户交互事件（如按钮点击、表单提交）中进行重定向。
**应用场景**: 适用于需要在特定用户交互事件触发后进行重定向的情况，例如：
- 用户点击按钮后重定向到另一个页面。
- 表单提交成功后重定向到确认页面。
**技术实现**:
- 使用 `useRouter` 钩子在事件处理函数中进行重定向。

## Browser History

这段话的意思是，在 `Next.js` 中，你可以使用浏览器的原生 `window.history.pushState` 和 `window.history.replaceState` 方法来更新浏览器的历史记录，而无需重新加载页面。同时，这些方法的调用会自动与 `Next.js` 的路由系统集成，从而保持与 `usePathname` 和 `useSearchParams` 钩子的同步。

### 详细解释

**使用原生方法更新历史记录**

浏览器的 `window.history.pushState` 和 `window.history.replaceState` 方法允许你在不重新加载页面的情况下，更新浏览器的地址栏 URL 和历史记录。这在单页应用（SPA）中非常常见。
    - `pushState`：添加一个新的历史记录条目。
    - `replaceState`：替换当前的历史记录条目。

**示例**：

```js
// 使用 pushState 添加新的历史记录条目
window.history.pushState({ page: 1 }, "title 1", "/page1");

// 使用 replaceState 替换当前的历史记录条目
window.history.replaceState({ page: 2 }, "title 2", "/page2");
```

**集成到 Next.js 路由器**

在 Next.js 中，当你使用 `pushState` 或 `replaceState` 方法时，这些操作会自动与 Next.js 的路由系统集成。这意味着你更新的 URL 会被 Next.js 识别并处理，就像你使用 Next.js 的路由器 API 一样。


## 路由和导航的工作原理

App Router 使用混合方法进行路由和导航。在服务器上，应用程序代码会自动按路由段进行代码拆分。在客户端上，Next.js预取和缓存路由段。这意味着，当用户导航到新路由时，浏览器不会重新加载页面，只有更改的路段会重新呈现，从而改善导航体验和性能。

### 代码拆分

+ 代码拆分允许您将应用程序代码拆分为更小的捆绑包，以便浏览器下载和执行。这减少了每个请求的传输数据量和执行时间，从而提高了性能。
+ 服务器组件允许应用程序代码按路由段自动进行代码拆分。这意味着导航时仅加载当前路由所需的代码。

### Prefetching

预取是一种在用户访问路由之前在后台预加载路由的方法。在 Next.js 中预取路由有两种方式：

+ `<Link>` 组件：当路由在用户视口中可见时，会自动预取路由。预取发生在页面首次加载或通过滚动进入视图时。
+ `useRouter.prefetch()` 可用于以编程方式预取路由。
+ `<Link>` 组件的默认预取行为（即，当 `prefetch` 属性未指定或设置为 `null` 时）会根据你是否使用了 `loading.js` 文件而有所不同。具体来说：
	- 只有共享布局以及从该共享布局到第一个 `loading.js` 文件之间的组件树会被预取并缓存 30 秒。
	- 这减少了获取整个动态路由的开销。
	- 这意味着你可以显示一个即时的加载状态，为用户提供更好的视觉反馈。

### caching

`Next.js`有一个称为路由器缓存的内存中客户端缓存。当用户在应用程序中导航时，预取路由段和访问路由的 React Server 组件有效负载存储在缓存中。

这意味着在导航时，缓存会尽可能多地重复使用，而不是向服务器发出新请求 - 通过减少请求和传输的数据数量来提高性能。


### 局部渲染

部分渲染意味着仅在客户端上重新渲染导航时更改的路段，并且保留所有共享路段。

例如，在两个同级路由之间导航时， `/dashboard/settings` `/dashboard/analytics` 将呈现 `settings` 和 `analytics` 页面，并保留共享 `dashboard` 布局。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fpartial-rendering.png&w=1920&q=75)

### 软导航

**硬导航（Hard Navigation）**:
- 传统的网页导航方式，浏览器会完全重新加载目标页面。
- 导致整个页面刷新，所有状态都会丢失。
- 浏览器会向服务器请求新的页面，加载新内容。

**软导航（Soft Navigation）**：
- 现代单页应用（SPA）常用的导航方式，只有需要更新的部分重新渲染。
- 保持页面的大部分内容不变，仅更新变化的部分。
- 保留客户端的状态，例如表单输入、应用状态等。

### Next.js 的软导航

Next.js 的 App Router 支持软导航，这带来了以下好处：

1. **部分呈现（Partial Rendering）**:
    - 仅重新呈现已更改的路由段，未变化的部分不会重新渲染。
    - 减少不必要的重新渲染，提高性能。
2. **保留客户端状态**:
    - 软导航过程中，客户端的 React 状态会被保留。
    - 例如，用户在一个页面填写表单时导航到另一个页面，然后返回时，表单内容不会丢失。

默认情况下，Next.js将保持向后和向前导航的滚动位置，并在路由器缓存中重用路由段。
