#!/bin/bash

# 博客文章生成脚本
# 用法: ./create_blog.sh <目录> <博客标题>
# 示例: ./create_blog.sh Database "Redis持久化机制"

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -ne 2 ]; then
    echo -e "${RED}错误: 参数不足${NC}"
    echo "用法: $0 <目录> <博客标题>"
    echo "示例: $0 Database \"Redis持久化机制\""
    echo ""
    echo "可用目录:"
    echo "  - Algorithm    (算法)"
    echo "  - Database     (数据库)"
    echo "  - Network      (网络)"
    echo "  - Docker       (容器)"
    echo "  - Linux        (Linux系统)"
    echo "  - Golang       (Go语言)"
    echo "  - JS           (JavaScript)"
    echo "  - C++          (C++)"
    exit 1
fi

CATEGORY=$1
TITLE=$2

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/${CATEGORY}"

# 检查目录是否存在，不存在则创建
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}目录 ${CATEGORY} 不存在，正在创建...${NC}"
    mkdir -p "$TARGET_DIR"
fi

# 生成文件名（使用拼音或英文）
# 这里简单处理，使用标题作为文件名，替换空格为下划线
FILENAME=$(echo "$TITLE" | sed 's/ /_/g').md
FILEPATH="${TARGET_DIR}/${FILENAME}"

# 检查文件是否已存在
if [ -f "$FILEPATH" ]; then
    echo -e "${RED}错误: 文件已存在: ${FILEPATH}${NC}"
    exit 1
fi

# 获取当前日期
CURRENT_DATE=$(date +%Y-%m-%d)

# 生成 permalink（小写，替换空格为-）
PERMALINK_TITLE=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/[^a-z0-9-]//g')
PERMALINK="/${CATEGORY,,}/${PERMALINK_TITLE}/"

# 生成博客模板
cat > "$FILEPATH" << EOF
---
title: ${TITLE}
createTime: ${CURRENT_DATE}
author: ZQ
tags:
  - TODO
description: TODO: 添加文章描述
permalink: ${PERMALINK}
---

> TODO: 添加文章概述（一句话总结文章核心内容）

<!-- more -->

## 概述

TODO: 详细介绍主题背景和重要性

## 核心概念

### 概念1

TODO: 解释核心概念

\`\`\`mermaid
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
\`\`\`

### 概念2

TODO: 继续解释

## 实现原理

### 原理1

TODO: 深入技术细节

\`\`\`
// 代码示例
function example() {
    return "Hello World";
}
\`\`\`

### 原理2

\`\`\`mermaid
sequenceDiagram
    participant A as 客户端
    participant B as 服务器
    
    A->>B: 请求
    B->>A: 响应
\`\`\`

## 实践案例

### 案例1

TODO: 提供实际应用场景

### 案例2

TODO: 更多案例

## 最佳实践

1. **实践1**: TODO
2. **实践2**: TODO
3. **实践3**: TODO

## 常见问题

### Q1: TODO 问题描述？

TODO: 回答

### Q2: TODO 问题描述？

TODO: 回答

## 总结

TODO: 总结文章要点

核心要点：
1. **要点1**: TODO
2. **要点2**: TODO
3. **要点3**: TODO

## 参考资料

- [TODO: 参考链接1](https://example.com)
- [TODO: 参考链接2](https://example.com)
EOF

echo -e "${GREEN}✓ 博客文章创建成功！${NC}"
echo -e "文件路径: ${FILEPATH}"
echo -e "分类: ${CATEGORY}"
echo -e "标题: ${TITLE}"
echo -e "Permalink: ${PERMALINK}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "1. 编辑文件填充 TODO 内容"
echo "2. 更新 tags 标签"
echo "3. 完善 description 描述"
echo "4. 添加 Mermaid 图表"
echo "5. 提交到 Git 仓库"
