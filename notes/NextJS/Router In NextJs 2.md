---
title: Streaming
createTime: 2024-7-8
author: ZQ
tags:
  - react
  - NextJs
description: NextJS App Router
permalink: /NextJS_AppRouter2/
---
<br> NextJS App Router
<!-- more -->
## 本篇笔记的结构

+ 加载UI和流式处理
+ 错误处理

## 加载UI和流式处理

这个特殊的文件 `loading.js` 可以帮助你使用React Suspense创建有意义的加载UI。使用此约定，您可以在加载路由段的内容时显示来自服务器的即时加载状态。渲染完成后，新内容将自动换入。


### Instant Loading Statesr

即时加载状态是后备 UI，在导航时立即显示。您可以预渲染加载指示器（如骨架和微调器），或未来屏幕的一小部分但有意义的部分，例如封面照片、标题等。这有助于用户了解应用正在响应，并提供更好的用户体验。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Floading-ui.png&w=1920&q=75)

通过在文件夹中添加 `loading.js` 文件来创建加载状态。

```tsx
export default function Loading() {
  // You can add any UI inside Loading, including a Skeleton.
  return <LoadingSkeleton />
}
```

在同一个文件夹中， `loading.js` 将嵌套在 `layout.js` .它会自动将 `page.js` 文件和下面的任何子项包装在 `<Suspense>` 边界中。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Floading-overview.png&w=1920&q=75)

> Tips:
+ 导航是即时的，即使使用以服务器为中心的路由也是如此。
+ 导航是可中断的，这意味着更改路线时无需等待路线内容完全加载，然后再导航到另一条路线。
+ 在加载新路由时，共享布局保持交互式。


## Streaming with Suspense

除了 `loading.js` 之外，您还可以为自己的 UI 组件手动创建悬念边界。App Router 支持 Node.js 和 Edge 运行时的 Suspense 流式传输。

### 什么是流媒体

要了解流式处理在 React 和 Next.js 中的工作原理，了解服务器端渲染 （SSR） 及其局限性会很有帮助。

使用服务器端渲染，在用户查看页面并与之交互之前，需要完成一系列步骤：
+ 首先，在服务器上获取给定页面的所有数据。
+ 然后，服务器渲染页面的 HTML。
+ 页面的 HTML、CSS 和 JavaScript 将发送到客户端。
+ 使用生成的 HTML 和 CSS 显示非交互式用户界面。
+ 最后，React 对用户界面进行水润，使其具有交互性。

这些步骤是连续的和阻塞的，这意味着服务器只能在获取所有数据后呈现页面的 HTML。而且，在客户端上，React 只有在下载了页面中所有组件的代码后才能对 UI 进行水化处理。

带有 React 和 Next.js 的 SSR 通过尽快向用户显示非交互式页面来帮助提高感知的加载性能。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fserver-rendering-without-streaming.png&w=1920&q=75)

但是，它仍然可能很慢，因为需要先完成服务器上的所有数据获取，然后才能向用户显示页面。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fserver-rendering-with-streaming.png&w=1920&q=75)

流式处理允许您将页面的 HTML 分解为更小的块，并逐步将这些块从服务器发送到客户端。
这样可以更快地显示页面的某些部分，而无需等待所有数据加载后才能呈现任何 UI。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fserver-rendering-with-streaming-chart.png&w=1920&q=75)

流式处理与 `React` 的组件模型配合得很好，因为每个组件都可以被视为一个块。具有更高优先级的组件（例如产品信息）或不依赖数据的组件可以先发送（例如布局），React 可以更早地开始水润。优先级较低的组件（例如评论、相关产品）在获取数据后可以在同一服务器请求中发送。

### Example

`<Suspense>` 其工作原理是包装执行异步操作的组件（例如获取数据），在执行异步操作时显示回退 UI（例如骨架、微调器），然后在操作完成后交换组件。

```tsx
import { Suspense } from 'react'
import { PostFeed, Weather } from './Components'
 
export default function Posts() {
  return (
    <section>
      <Suspense fallback={<p>Loading feed...</p>}>
        <PostFeed />
      </Suspense>
      <Suspense fallback={<p>Loading weather...</p>}>
        <Weather />
      </Suspense>
    </section>
  )
}
```

通过使用 Suspense，您可以获得以下好处：

+ 流式处理服务器渲染 - 从服务器到客户端的渐进式渲染 HTML。
+ 选择性水合作用 - React 根据用户交互优先确定哪些组件的优先级。

### SEO 搜索引擎优化

+ `Next.js`将等待内部 `generateMetadata` 数据提取完成，然后再将 UI 流式传输到客户端。这保证了流式响应的第一部分包含 `<head>` 标记。

## Error Handling 错误处理

### 概述

文件 `error.js` 约定允许您在嵌套路由中正常处理意外的运行时错误。

+ 自动将路由段及嵌套的子段包装在React错误边界中。
+ 使用文件系统层次结构创建针对特定段量身定制的错误 UI，以调整粒度。
+ 将错误隔离到受影响的段，同时保持应用程序的其余部分正常运行。
+ 尝试在不重新加载整页的情况下从错误中恢复。

通过在路由段中添加 `error.js` 文件并导出 React 组件来创建错误 UI：

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Ferror-special-file.png&w=1920&q=75)

```tsx
'use client' // Error components must be Client Components
 
import { useEffect } from 'react'
 
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])
 
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button
        onClick={
          // Attempt to recover by trying to re-render the segment
          () => reset()
        }
      >
        Try again
      </button>
    </div>
  )
}
```

###  `error.js` 是怎么工作的

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Ferror-overview.png&w=1920&q=75)

 + `error.js` 自动创建一个 React 错误边界，用于包装嵌套的子段或 `page.js` 组件。
 + 从 `error.js` 文件导出的 React 组件用作回退组件。
 + 如果在错误边界内引发错误，则包含该错误，并呈现回退组件。
 + 当回退错误组件处于活动状态时，错误边界上方的布局将保持其状态并保持交互状态，并且错误组件可以显示从错误中恢复的功能。

### 从错误中恢复

+ 错误的原因有时可能是暂时的。在这些情况下，只需重试即可解决问题。
+ 错误组件可以使用该 `reset()` 函数提示用户尝试从错误中恢复。执行时，该函数将尝试重新呈现 Error 边界的内容。如果成功，则回退错误组件将替换为重新渲染的结果。

## 嵌套路由

+ 通过特殊文件创建的 React 组件呈现在特定的嵌套层次结构中。
+ 例如，包含两个段（包含 `layout.js` 和 `error.js` 文件）的嵌套路由呈现在以下简化的组件层次结构中:
   ![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fnested-error-component-hierarchy.png&w=1920&q=75)

+ 嵌套组件层次结构对嵌套路由中的 `error.js` 文件行为有影响：
+ 错误会冒泡到最近的父错误边界。这意味着文件 `error.js` 将处理其所有嵌套子段的错误。通过将不同级别的文件放置 `error.js` 在路由的嵌套文件夹中，可以实现或多或少的粒度错误 UI。
+ 边界 `error.js` 不会处理在同一段中的 `layout.js` 组件中引发的错误，因为错误边界嵌套在该布局的组件中。

### 布局中的错误

+ 根 `app/error.js` 边界不会捕获根 `app/layout.js` 边界或 `app/template.js` 组件中引发的错误。
+ 若要专门处理这些根组件中的错误，请使用位于根 `app` 目录中的 `error.js` 的变体`app/global-error.js`。
+ 与根 `error.js` 不同， `global-error.js` 错误边界包装整个应用程序，其回退组件在活动时替换根布局。因此，需要注意的是， `global-error.js` 必须定义自己的 `<html>` 和 `<body>` 标签。
+ `global-error.js` 是粒度最小的错误 UI，可以被视为整个应用程序的“包罗万象”错误处理。它不太可能经常被触发，因为根组件通常不太动态，而其他 `error.js` 边界将捕获大多数错误。
+ 即使定义了 a `global-error.js` ，仍建议定义一个根 `error.js` ，其回退组件将在根布局中呈现，其中包括全局共享的 UI 和品牌。

>Tips:
+ `global-error.js` 仅在生产环境中启用。在开发中，我们的错误叠加将显示出来。

## 服务器错误

+ 如果在服务器组件中抛出错误，Next.js 会将一个 `Error` 对象（在生产中剥离了敏感错误信息）作为 `error` prop 转发到最近的 `error.js` 文件。‘
+ 在生产过程中，转发到客户端的 `Error` 对象仅包含泛型 `message` 和 `digest` 属性。
+ 该 `message` 属性包含有关错误的一般消息，该 `digest` 属性包含自动生成的错误哈希，可用于匹配服务器端日志中的相应错误。
+ 在开发过程中，转发到客户端的 `Error` 对象将被序列化，并包含 `message` 原始错误，以便于调试。
