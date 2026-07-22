---
name: how-to-add-cover-pic-for-blog
description: >-
  为技术博客生成封面插画的 nano-banana 提示词：做成「现代扁平信息图」风格——专业友好、明亮但不幼稚、带醒目标题与关键标注、一眼看懂主题。明确每个元素在画面中的位置，横向 16:9 输出，并写入本地临时文件（不进版本库）。
  在用户要求为博文生成封面 / 插画 / 配图提示词时使用。
disable-model-invocation: false
---

# 为博客生成封面插画提示词

## 产物

- **一条 nano-banana 提示词**（自然语言、英文、叙述式）。
- 写入**本地临时文件**，不提交版本库（见「产物文件」）。

## 风格基调：现代扁平信息图（flat explainer）

目标是**一眼看懂主题**、且**专业不幼稚**。基调参照高质量技术 explainer 配图：

- **现代扁平矢量风**（flat / slightly geometric vector），干净细描边，不要 3D、不要厚涂、不要过度可爱的大眼萌物。
- **明亮但克制**的配色：蓝 / 黄 / 绿等清爽色，低饱和、专业感，避免糖果色幼态。
- **带醒目大标题**点明主题；关键组件配**短标注**，必要时用箭头表达流程 / 对比 / 层次。
- 拟人/表情**克制使用**：最多用极简符号（✓ / ✗、稳/抖的姿态）暗示状态，不画笑脸大眼吉祥物。

> 四个高频错误：① 太萌太卡通（像儿童贴纸）→ 改用扁平专业风；② 出成方形/竖图 → 必须横向 16:9，元素沿水平方向铺开；③ 太抽象（如一堆无意义的彩色圆点）→ 用**有方向、有状态**的具象隐喻（带箭头的轨道、排队的任务卡、高亮「正在运行」的对象），让机制一眼可读；④ 太像干巴巴的架构图（方块+箭头+标签）→ 给**插画质感与场景感**：等距立体、柔和阴影/渐变、把概念画成有细节的具象物件和动作（而非平面色块）。

## 关键原则：明确「在哪里画什么」+ 横向构图

- **逐元素定位**：提示词里写清每个元素在画面的**确切位置**（顶部居中标题、左半 / 右半、中央、底部标注），不让模型自由发挥。
- **强制横向**：明确 `wide 16:9 landscape`，元素**横向铺开**填满宽画幅，避免挤成正方形。
- **文字短、英文、给确切拼写**：1 个标题 + 2–4 个短标注，用引号给出原文，控制数量防止画乱。

## 提示词模板

```text
A modern flat infographic illustration explaining <主题一句话>, clean professional vector explainer style, wide 16:9 landscape composition with elements spread horizontally.

LAYOUT (exact placement):
- Top center: a bold title reading "<TITLE>".
- <左/中/右/底部，逐个元素：在哪里、画什么、标注什么文字、箭头从哪到哪>.

STYLE: flat vector, clean thin outlines, bright but muted professional palette (blue, yellow, green), subtle flat shading, minimal symbols (no big cartoon faces). Well-organized, balanced, easy to read at a glance, wide horizontal layout.
Use only the short English labels spelled exactly as written above.
```

只替换 `<...>` 处，其余措辞保持不变以维持风格统一。

## 产物文件

- 路径：博客仓库下 `covers/<博文文件名>.prompt.txt`（一篇一文件）。
- `covers/` 已被 `.gitignore` 忽略——提示词是本地中间产物，留在本地、不入库。
