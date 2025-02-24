---
title: Project Organization
createTime: 2024-7-10
author: ZQ
tags:
  - react
  - NextJs
description: This note records things about Project Organization.
---
 This note records things about Project Organization.
<!-- more -->
## 默认安全托管

在 `app` 目录中，嵌套文件夹层次结构定义路由结构。

每个文件夹表示映射到 URL 路径中相应区段的路由段。

但是，即使路由结构是通过文件夹定义的，在将 `page.js` or `route.js` 文件添加到路由段之前，路由也无法公开访问。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-not-routable.png&w=1920&q=75)

而且，即使路由可公开访问，也只有客户端 `page.js` 返回或 `route.js` 发送给客户端的内容。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-routable.png&w=1920&q=75)

这意味着项目文件可以安全地位于 `app` 目录中的路由段内，而不会意外地被路由。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-colocation.png&w=1920&q=75)

>Tips:
+ 这与 `pages` 目录不同，在目录中，任何文件都 `pages` 被视为路由。
+ 虽然您可以将项目文件托管在一起 `app` ，但不必这样做。如果您愿意，可以将它们保留在 `app` 目录之外。

## 项目组织

Next.js提供了多种功能来帮助您组织项目。

### Private Folders

可以通过在文件夹前加上下划线来创建专用文件夹： `_folderName`

这表示该文件夹是私有实现详细信息，路由系统不应考虑该文件夹，从而选择该文件夹及其所有子文件夹退出路由。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-private-folders.png&w=1920&q=75)

由于默认情况下可以安全地共置 `app` 目录中的文件，因此不需要专用文件夹进行共置。但是，它们可用于：

+ 将 UI 逻辑与路由逻辑分离。
+ 始终如一地组织整个项目和Next.js生态系统的内部文件。
+ 在代码编辑器中对文件进行排序和分组。
+ 避免与将来的 Next.js 文件约定发生潜在的命名冲突。

> Tips:

+ 虽然不是框架约定，但您也可以考虑使用相同的下划线模式将专用文件夹外的文件标记为“专用”。
+ 您可以创建以下划线开头的 URL 段，方法是在文件夹名称前面加上 `%5F` （下划线的 URL 编码形式）： `%5FfolderName` 。
+ 如果您不使用专用文件夹，了解Next.js特殊的文件约定以防止意外的命名冲突会很有帮助。

## Src 目录

Next.js支持将应用程序代码（包括 `app` ）存储在可选 `src` 目录中。这将应用程序代码与项目配置文件分开，这些文件主要位于项目的根目录中。

## 模块路径别名

Next.js支持模块路径别名，可以更轻松地读取和维护深度嵌套项目文件的导入。

```js
// before
import { Button } from '../../../components/button'
 
// after
import { Button } from '@/components/button'
```

## 项目组织策略

+ 在Next.js项目中组织自己的文件和文件夹时，没有“正确”或“错误”的方法。
+ 以下部分列出了常见策略的高级概述。最简单的要点是选择适合您和您的团队的策略，并在整个项目中保持一致。

>Tips
+ 很高兴知道：在下面的示例中，我们使用 `components` 和 `lib` 文件夹作为通用占位符，它们的命名没有特殊的框架意义，您的项目可能会使用其他文件夹，如 `ui` 、 `utils` 、 `hooks` `styles` 等。
## 将项目文件存储在`APP`外面

此策略将所有应用程序代码存储在项目根目录的共享文件夹中，并保留该 `app` 目录纯粹用于路由目的。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-project-root.png&w=1920&q=75)

## 将项目文件存储在`APP`内部

此策略将所有应用程序代码存储在 `app` 目录根目录的共享文件夹中。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-app-root.png&w=1920&q=75)

### 按功能或路由拆分文件

此策略将全局共享的应用程序代码存储在根 `app` 目录中，并将更具体的应用程序代码拆分为使用它们的路由段。

![](https://nextjs.org/_next/image?url=%2Fdocs%2Flight%2Fproject-organization-app-root-split.png&w=1920&q=75)
