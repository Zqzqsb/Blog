---
name: how-to-put-cover-on-blog
description: >-
  把博文封面挂到 VuePress Plume 列表与正文：用 more 前的 Markdown 图铺满摘要栏（STL 文那种），
  不要用 frontmatter cover 当「标题下通栏」。在用户要求加封面 / 列表插画 / 封面位置 / cover
  字段、或生成封面后要写进文章时使用。
disable-model-invocation: false
---

# 把封面挂到博文

目标列表卡：**标题 + 元信息 → 与摘要同宽的通栏图 → 引言**。参照 `Programming/Multi-Threading/STL 容器的线程安全性讨论.md`。

出图提示词走 [how-to-add-cover-pic-for-blog](../how-to-add-cover-pic-for-blog/SKILL.md)。本技能只管**怎么挂、怎么发**。

## 标准写法（默认）

1. 16:9 JPEG 放到仓库 `public/images/<slug>-cover.jpg`（或已有 OSS URL）。
2. 正文 frontmatter **不要**写 `cover` / `coverStyle` / 手写 `excerpt`。
3. 标题后立刻：图 → 引言引用 → `<!-- more -->`。

```markdown
---
title: …
createTime: YYYY-MM-DD
author: ZQ
tags: […]
permalink: /…/…
---

![](/images/<slug>-cover.jpg)

> 一句话定义 + 为什么值得关心。

<!-- more -->
```

列表和正文都会出这张图。这是预期，与 STL 文一致。

Jenkins 构建会把仓库 `public/` 拷到 `docs/.vuepress/public/`，所以 Markdown 里必须用**站点绝对路径** `/images/…` 或远程 URL。`.assets/` 相对路径、以及 Plume `cover:` 相对路径，列表都不可靠。

## 不要做

| 做法 | 结果 |
| --- | --- |
| frontmatter `cover:` + `<!-- more -->` 前再放一张图 | 列表双图 |
| `coverStyle.layout: top` | 图在**标题上方**铺满，过高 |
| `coverStyle.layout: right`（默认 4:3 或窄 16:9） | 流程图被裁或缩成看不清 |
| 手写 `excerpt` 塞 `<img style="max-height:…">` | 左对齐留白或缩在中间，不像封面 |
| 只改 Plume 组件源码 | 不必要；标准写法不碰主题 |

Plume 的 `cover` **只作用于列表**，且 `layout` 只有 `left | right | odd-left | odd-right | top`，没有「标题下面」。要标题下通栏，用上面的 Markdown，不要用 `cover` 字段。

## 出图之后

- 提示词文件写在 `covers/<博文文件名>.prompt.txt`（gitignore，不入库）。
- 成品图入库：`public/images/<slug>-cover.jpg`。
- 提交博文 Markdown + `public/images/` 下的图。

## 发布与核对

```bash
# 仓库已 push 后，在本机构建机执行
docker exec -w /var/jenkins_home/workspace/GenBlog/Vuepress/blog jenkins git reset --hard
docker exec -w /var/jenkins_home/workspace/GenBlog/Vuepress -e CI=true jenkins bash gen_blog_dist.sh
```

打开 https://blog.zqzqsb.cn/blog/ ：该卡应是标题 → 通栏图 → 引言，图宽与引言块对齐，不被裁切。
