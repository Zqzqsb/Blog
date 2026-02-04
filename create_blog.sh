#!/bin/bash

# 博客文章生成脚本 - 交互式版本
# 用法: ./create_blog.sh
# 支持多级目录选择，输入 q 或 exit 随时退出

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查退出命令
check_exit() {
    if [[ "$1" == "q" ]] || [[ "$1" == "exit" ]] || [[ "$1" == "quit" ]]; then
        echo -e "${YELLOW}已取消操作${NC}"
        exit 0
    fi
}

# 全局计数器
GLOBAL_COUNTER=1

# 扫描目录结构，生成树形列表
# 参数: $1 = 基础路径, $2 = 缩进级别
scan_directories() {
    local base_path="$1"
    local indent_level="${2:-0}"
    local indent=""
    
    # 生成缩进
    for ((i=0; i<indent_level; i++)); do
        indent="  ${indent}"
    done
    
    # 排除的目录
    local exclude_dirs=(".git" "node_modules" ".obsidian" "Notes" ".windsurf")
    
    for item in "$base_path"/*; do
        if [ -d "$item" ]; then
            local dir_name=$(basename "$item")
            
            # 检查是否在排除列表中
            local should_exclude=false
            for exclude in "${exclude_dirs[@]}"; do
                if [[ "$dir_name" == "$exclude" ]]; then
                    should_exclude=true
                    break
                fi
            done
            
            if [ "$should_exclude" = false ]; then
                local relative_path="${item#$SCRIPT_DIR/}"
                
                # 检查是否有子目录
                local has_subdirs=false
                for subitem in "$item"/*; do
                    if [ -d "$subitem" ]; then
                        local subdir_name=$(basename "$subitem")
                        local sub_exclude=false
                        for exclude in "${exclude_dirs[@]}"; do
                            if [[ "$subdir_name" == "$exclude" ]]; then
                                sub_exclude=true
                                break
                            fi
                        done
                        if [ "$sub_exclude" = false ]; then
                            has_subdirs=true
                            break
                        fi
                    fi
                done
                
                # 存储目录信息并显示
                DIR_MAP["$GLOBAL_COUNTER"]="$relative_path"
                
                if [ "$has_subdirs" = true ]; then
                    echo -e "${indent}${CYAN}${GLOBAL_COUNTER}. ${dir_name}/${NC}"
                    ((GLOBAL_COUNTER++))
                    
                    # 递归扫描子目录
                    for subitem in "$item"/*; do
                        if [ -d "$subitem" ]; then
                            local subdir_name=$(basename "$subitem")
                            local sub_exclude=false
                            for exclude in "${exclude_dirs[@]}"; do
                                if [[ "$subdir_name" == "$exclude" ]]; then
                                    sub_exclude=true
                                    break
                                fi
                            done
                            if [ "$sub_exclude" = false ]; then
                                local sub_relative_path="${subitem#$SCRIPT_DIR/}"
                                DIR_MAP["$GLOBAL_COUNTER"]="$sub_relative_path"
                                echo -e "${indent}  ${GLOBAL_COUNTER}. ${subdir_name}"
                                ((GLOBAL_COUNTER++))
                            fi
                        fi
                    done
                else
                    echo -e "${indent}${GLOBAL_COUNTER}. ${dir_name}"
                    ((GLOBAL_COUNTER++))
                fi
            fi
        fi
    done
}

# 关联数组存储目录映射
declare -A DIR_MAP

# 显示目录选择菜单
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}博客文章创建工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}可用目录:${NC}"
echo ""

# 扫描并显示目录
scan_directories "$SCRIPT_DIR" "" ""

echo ""
echo -e "${YELLOW}提示: 输入 'q' 或 'exit' 随时退出${NC}"
echo ""

# 选择目录
while true; do
    echo -ne "${GREEN}请选择目录编号: ${NC}"
    read -r selection
    check_exit "$selection"
    
    if [[ -n "${DIR_MAP[$selection]}" ]]; then
        CATEGORY="${DIR_MAP[$selection]}"
        echo -e "${GREEN}✓ 已选择: ${CATEGORY}${NC}"
        break
    else
        echo -e "${RED}错误: 无效的编号，请重新输入${NC}"
    fi
done

echo ""

# 输入博客标题
while true; do
    echo -ne "${GREEN}请输入博客标题: ${NC}"
    read -e -r TITLE
    check_exit "$TITLE"
    
    if [[ -z "$TITLE" ]]; then
        echo -e "${RED}错误: 标题不能为空${NC}"
    else
        echo -e "${GREEN}✓ 标题: ${TITLE}${NC}"
        break
    fi
done

echo ""

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
