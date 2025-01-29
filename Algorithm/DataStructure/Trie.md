---
title: Trie
createTime: 2025-1-29
tags:
- 字典树
author: ZQ
permalink: /algorithm/ds/trie/
---

本文讲解了字典树的结构和实现方法。字典树是一种用于处理字符串集合的数据结构，特别适用于前缀查询和自动补全等应用。

<!-- more -->

## 概述

字典树（Trie）是一种树形数据结构，用于高效地存储和检索字符串集合中的键。每个节点代表一个字符，边表示字符之间的连接。字典树的根节点通常是空的，叶子节点代表一个完整的字符串。

字典树的主要操作包括插入、删除和查找。通过逐字符插入或查找，字典树能够在 `O(L)` 时间复杂度内完成操作，其中 `L` 是字符串的长度。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Trie/Trie.png)

## 代码示例

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

### 使用字符数组

```cpp
#include <iostream>
#include <cstring> // 用于 memset
#include <string>

using namespace std;

// 定义 Trie 的节点结构
struct TreeNode {
    TreeNode* children[26]; // 子节点数组，存储 'a' 到 'z'
    int count;              // 以当前节点为结尾的字符串计数

    TreeNode() : count(0) {
        memset(children, 0, sizeof(children)); // 初始化子节点为 nullptr
    }
};

// 插入字符串到 Trie 中
void insert(TreeNode* root, const string& str) {
    TreeNode* node = root;
    for (char c : str) {
        int index = c - 'a'; // 将字符映射到 0-25 的索引
        if (!node->children[index]) {
            node->children[index] = new TreeNode(); // 如果不存在对应子节点，则创建
        }
        node = node->children[index];
    }
    node->count++; // 增加当前节点的字符串计数
}

// 查询字符串在 Trie 中的计数
int query(TreeNode* root, const string& str) {
    TreeNode* node = root;
    for (char c : str) {
        int index = c - 'a'; // 将字符映射到 0-25 的索引
        if (!node->children[index]) {
            return 0; // 未找到字符串
        }
        node = node->children[index];
    }
    return node->count; // 返回以该节点为结尾的字符串计数
}

// 递归释放 Trie 所有节点的内存
void destroy(TreeNode* node) {
    for (int i = 0; i < 26; ++i) {
        if (node->children[i]) {
            destroy(node->children[i]);
        }
    }
    delete node;
}

int main() {
    int n;
    cin >> n;

    TreeNode* root = new TreeNode(); // 创建根节点

    while (n--) {
        char op;
        string str;
        cin >> op >> str;

        if (op == 'I') {
            insert(root, str);
        } else if (op == 'Q') {
            cout << query(root, str) << endl;
        }
    }

    destroy(root); // 释放内存
    return 0;
}
```

### 使用数组模拟

+ 数组的一行存储树的一层，层之间的跳转关系存储在每行的具体位置上。
+ 存储的效率事实上和第二种写法相当。

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