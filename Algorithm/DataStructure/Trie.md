---
title: Trie
createTime: 2025-1-29
tags:
- 字典树
author: ZQ
permalink: /algorithm/ds/trie/
---

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Trie/Trie.png)

本文讲解了字典树的结构和实现方法。字典树是一种用于处理字符串集合的数据结构，特别适用于前缀查询和自动补全等应用。

<!-- more -->

## 概述

字典树（Trie）是一种树形数据结构，用于高效地存储和检索字符串集合中的键。每个节点代表一个字符，边表示字符之间的连接。字典树的根节点通常是空的，叶子节点代表一个完整的字符串。

字典树的主要操作包括插入、删除和查找。通过逐字符插入或查找，字典树能够在 `O(L)` 时间复杂度内完成操作，其中 `L` 是字符串的长度。

## 常用操作

### 插入（Insert）

**功能**：将一个字符串插入到 Trie 中。

**实现思路**：

- 从根节点开始，逐字符遍历字符串。
- 对于每个字符，如果对应的子节点不存在，则创建一个新的子节点。
- 遍历完所有字符后，标记当前节点为字符串的结束节点，并更新计数。

### 2. 删除（Delete）

**功能**：从 Trie 中移除一个字符串。

**实现思路**：

- 从根节点开始，逐字符遍历字符串，同时记录路径上的节点。
- 如果字符串存在，减少计数并取消结束标记。
- 回溯路径，删除不再需要的节点（即没有子节点且不是其他字符串的结束节点）。

### 3. 查找（Search）

**功能**：判断一个字符串是否存在于 Trie 中。

**实现思路**：

- 从根节点开始，逐字符遍历字符串。
- 如果某个字符的子节点不存在，则字符串不存在。
- 遍历完所有字符后，检查当前节点是否为字符串的结束节点。

### 4. 前缀查询（Prefix Search）

**功能**：判断 Trie 中是否存在以某个前缀开头的字符串。

**实现思路**：

- 从根节点开始，逐字符遍历前缀字符串。
- 如果某个字符的子节点不存在，则不存在以该前缀开头的字符串。
- 如果成功遍历整个前缀，说明存在至少一个以该前缀开头的字符串。

## 代码示例

示例代码中仅仅实现了插入和查找。
### 使用哈希表维护下一层节点

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

using namespace std;

// Define the TreeNode structure
struct TreeNode {
    unordered_map<char, TreeNode*> children; // Map each character to its child node
    int count; // Store the number of strings that end at this node
    TreeNode() : count(0) {} // Constructor to initialize count to 0
};

// Trie class for better encapsulation
class Trie {
private:
    TreeNode* root;

public:
    Trie() {
        root = new TreeNode(); // Initialize root node
    }

    // Insert a string into the Trie
    void insert(const string& str) {
        TreeNode* node = root;
        for (char c : str) {
            if (node->children.find(c) == node->children.end()) {
                node->children[c] = new TreeNode();
            }
            node = node->children[c];
        }
        node->count++; // Mark the end of a string
    }

    // Query the count of a specific string in the Trie
    int query(const string& str) {
        TreeNode* node = root;
        for (char c : str) {
            if (node->children.find(c) == node->children.end()) {
                return 0; // String not found
            }
            node = node->children[c];
        }
        return node->count; // Return the count of strings that end at this node
    }

    // Destructor to free allocated memory
    ~Trie() {
        destroy(root);
    }

private:
    // Helper function to recursively delete nodes
    void destroy(TreeNode* node) {
        for (auto& child : node->children) {
            destroy(child.second);
        }
        delete node;
    }
};
```

### 使用数组模拟

+ 数组的一行存储树的一层，层之间的跳转关系存储在每行的具体位置上。

```cpp
#include <iostream>
using namespace std;

const int N = 100010;

// trie树是一棵字典树 其最大深度为N 每一行都有26个可用节点
// cnt 存储以某个标号结尾的字符有多少个 idx是字符
int tree[N][26] , cnt[N] , idx;
char str[N];

void insert(char str[])
{
    int p = 0;
    for(int i = 0 ; str[i] ; i++)
    {
        int u = str[i] - 'a';
        // 如果该位置没有标号 那么赋一个新的标号给它
        // 如果这个位置有标号 那么重复利用该标号
        if(!tree[p][u]) tree[p][u] = ++idx;
        p = tree[p][u]; // 进入树的下一层 层次是由标号确定的。
    }
    cnt[p]++;
}
int query(char str[])
{
    int p = 0;
    for(int i = 0 ; str[i] ; i++)
    {
        int u = str[i] - 'a';
        if(!tree[p][u]) return 0;
        else p = tree[p][u];
    }
    return cnt[p];
}

int main()
{
    int n;
    cin >> n;
    
    char op;
    
    while(n--)
    {
        cin >> op;
        scanf("%s" , str);
        
        if(op == 'I') insert(str);
        else cout << query(str) << endl;
    }
}
```