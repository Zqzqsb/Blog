---
title: Simulate Linked List
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/Linked-list.png
createTime: 2024-4-24
description: 本文讲解了C++链表的结构体实现方法和模拟数组实现方法。
author: ZQ
permalink: /algorithm/basic/linked_list/
---
![cover]( https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/Linked-list.png)
<br> 本文讲解了C++链表的结构体实现方法和模拟数组实现方法。
<!-- more -->

## 链表结构

链表属于逻辑线性表的一种，它由一系列称为节点（Node）的元素组成，每个节点包含数据和指向下一个节点的指针（或引用）。

链表中的节点可以在内存中以任意顺序分散存储，而不像数组那样需要连续的内存空间。每个节点除了存储数据外，还包含指向下一个节点的指针，通过这种方式链接起所有节点，形成一个链式结构。

## 虚拟头部

![virtual_head](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/virtual_head.png)

>链表的虚拟头部，也被称为虚拟头节点或哑节点（dummy node），是一个不存在实际数据的节点，它通常被添加到链表的头部。虚拟头节点的主要目的是简化链表操作，特别是对于在链表头部插入和删除节点的操作。

>以下是使用虚拟头节点的一些好处：

+ 统一操作：在不使用虚拟头节点的情况下，插入和删除操作需要根据节点的位置（头部、中间、尾部）进行不同的处理。但如果使用了虚拟头节点，由于头部总有一个节点存在（虚拟头节点），所以插入和删除操作可以统一处理，无需对头节点做特殊处理。

+ 简化代码：由于操作统一，可以减少对特殊情况的处理，使得代码更简洁，易于理解和维护。

+ 边界处理：在一些复杂的链表操作中，例如链表的反转、合并等，使用虚拟头节点可以简化边界条件的处理，避免出错。

## 操作动画

> 动画来自[数据结构和算法可视化](https://visualgo.net/en)。

### 头部插入

![head](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/insert_head.gif)

### 尾部插入

![append](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/append.gif)

### 指定位置插入

![insert](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/insert.gif)

### 指定位置删除

![delete](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/basic/linked_list/delete.gif)


## 使用class构造链表(有虚拟头部)

可以在本地运行以下代码.

```c++
#include <iostream>
#include <vector>
using namespace std;

template<typename T>
struct Node
{
    T data;
    Node<T>* next;
};

// linked-list with virtual head
template<typename T>
class SingleLinkedList
{
    Node<T>* head;
public:
    // no parameter constructor create Head only
    SingleLinkedList()
    {
        this -> head = new Node<T>;
        this -> head -> next = nullptr;
    }
    
    // head inserter
    SingleLinkedList(const vector<T> &v , bool Reverse = true)
    {   
        head = new Node<T>;
        head -> next = nullptr;
        if(Reverse)
        {
            Node<T>* temp;
            for(auto i : v)
            {
                temp = new Node<T>;
                temp -> data = i;
                temp -> next = head -> next;
                head -> next = temp;
                
            }
        }
        else
        {
            Node<T> *temp , *work = head;
            for(auto i : v)
            {
                temp = new Node<T>;
                temp -> data = i;
                // keep work pointer at the end of the list
                work -> next = temp;
                work = work -> next;
            }
            work -> next = nullptr;
        }
    }
    
    // 析构函数
    ~SingleLinkedList()
    {
        cout << endl << "deleting whole linked list:" << endl;
        Node<T> *work = head -> next;
        while(head != nullptr)
        {
            cout << "delete " << head -> data << endl;
            delete head;
            head = work;
            if(head) work = head -> next;
        }
    }
    
    // 头插
    void insertHead(const T &data)
    {
        Node<T>* toInsert = new Node<T>;
        toInsert -> data = data;
        
        toInsert -> next = head -> next;
        head -> next = toInsert;
    }

    // 尾插
    void append(const T &data)
    {
        Node<T> *toAppend = new Node<T>;
        toAppend -> data = data;
        toAppend -> next = nullptr;
        
        Node<T> *p = this -> head;
        while(p -> next) p = p -> next;
        p -> next = toAppend;
    }
    
    // 删除一个特定位置的元素
    // k 属于 [1 , n] , n为链表的长度
    bool delete_k(int k)
    {
        Node<T>* p = head;

        // 定位到p的前一个为止
        while(p -> next && --k)
        {
            p = p -> next;
        }
        if(p -> next  == nullptr) return false;
        else
        {
            Node<T>* q = p -> next;
            p -> next = q -> next;
            delete q;
            return true;
        }
    }
    
    // 从下标获得元素
    Node<T>* getElement(int index)
    {
        if (index == 0)
            return head;
        if(index < 1)
            return NULL;

        int i = 1;
        Node<T>* work = head -> next;
        while(i < index && work != nullptr)
        {
            work = work -> next;
            i++;
        }
        return work; // if index > i , return nullptr
        
    }

    // 定位元素
    Node<T>* LocateElement(const T& e)
    {
        Node<T>* work = head -> next;
        while(work != nullptr && work -> data != e)
            work = work -> next;
        return work;
    }

    // 翻转
    void reverse()
    {
        Node<T>* work = head -> next;
        Node<T>* work_next;
        head -> next = nullptr;
        while(work != nullptr)
        {
            work_next = work -> next;
            work -> next = head -> next;
            head -> next = work;
            work = work_next;
        }
    } 
    
    // 打印
    void print()
    {
        Node<T>* work = head -> next;
        while(work != nullptr)
        {
            cout << work->data << " ";
            work = work -> next;
        }
        cout << endl;
        return;
    }
};

void print_separator()
{
    cout << "--------------------------------" << endl;
}

int main()
{
    // test constructor
    vector<int> v({1, 2, 3, 4, 5, 6, 7, 8, 9});
    SingleLinkedList<int> sll(v , true);
    cout << "linked list:";
    sll.print();

    // test getElement
    print_separator();
    cout << "get data index at 5: " << sll.getElement(5) -> data << endl;

    // test locaterElement
    print_separator();
    cout << "locate data 6 in list: " <<  sll.LocateElement(6) -> data << endl;   

    // test reverse
    print_separator();
    cout << "after reverse:" << endl;
    sll.reverse();
    sll.print();

    // test insert head
    print_separator();
    cout << "insert head 100:" << endl;
    sll.insertHead(100);
    sll.print();

    // test insert tail
    print_separator();
    cout << "insert tail 100:" << endl;
    sll.append(100);
    sll.print();
    
    // test delete_k
    print_separator();
    cout << "delete at position 5:" << endl;
    sll.delete_k(5);
    sll.print();
    
    print_separator();
}
```

## 使用数组模拟链表

### 理由

在算法竞赛中，频繁在堆区开辟和删除空间。

+ `Node* p = new Node;`
+ `delete p`

这两个操作是十分耗时的，所以在处理链表时，一般我们采用模拟数组的方法。下面给出写法。

### 方法

```c++
#include<iostream>
using namespace std;

const int N = 1e5; // 规定了链表可用的空间数量
// head 表示一个链表的头结点在 e数组中的位置 
// e[head] 是 head的值 对应结构体中的 head -> data
// ne[head] 是 head -> next 在 e中的位置。
// 可以类推 e 数组存储了 每个节点的数据 而 ne数组存储了 下一节点的位置
// head = -1 意味着 head -> next = nullptr 当 ne[i] = -1 代表访问到了链表最后一个位置。
int e[N] , ne[N] , head = -1 , idx = 1; 

// 头插法
void insert_head(int x)
{
    e[idx] = x;
    ne[idx] = head;
    head = idx++;
}

void insert_tail(int x)
{
    int p = head;
    while(ne[p] != -1)
        p = ne[p];
    e[idx] = x;
    ne[idx] = ne[p];
    ne[p] = idx++;
}

void print_linked_list()
{
    int p = head;
    while(p != -1)
    {
        cout << e[p] << " ";
        p = ne[p];
    }
    cout << endl;
}

int main()
{
    insert_head(1);
    insert_head(2);
    insert_tail(100);
    insert_tail(200);
    print_linked_list();
}
```

### 要点

+ 这个链表没有使用虚拟头部。
+ 在这种存储模式下 idx标记了当前空间使用到哪里,当某个链表节点被删除时,它所对应的空间将不再被使用。
+ 若idx的初始值为1，那么idx的值标志着e[idx]插入数组的序号。
+ 操作的逻辑和使用结构体完全一致。


### 试一试

[模拟链表操作](https://geniuscode.tech/problem/%E7%AE%97%E6%B3%95%E5%9F%BA%E7%A1%80-%E9%93%BE%E8%A1%A8-%E9%93%BE%E8%A1%A8%E6%93%8D%E4%BD%9C1)

**解法一 结构体**

```c++
#include<iostream>
#include<string>
using namespace std;

struct Node
{
    int data;
    Node* next;    

    Node(int x = 0): data(x) , next(nullptr) {} 
};

Node* vHead = new Node();

// 头插法
void insert_head(int x)
{
    Node* temp = new Node(x);
    temp -> next = vHead -> next;
    vHead -> next = temp;
}

// 在index之前插入
bool insert_index(int index , int x)
{
    Node* p = vHead;
    while(p != nullptr && --index)
    {
        p = p -> next;
    }

    if(p == nullptr) return false;
    
    Node* temp = new Node(x);
    temp -> next = p -> next;
    p -> next = temp;
    return true;
}

bool delete_index(int index)
{
    Node* p = vHead;
    // 定位到index的前一个
    while(p != nullptr && --index)
    {
        p = p -> next;
    }
    
    if(p == nullptr || p -> next == nullptr) return false;
    
    p -> next = p -> next -> next;
    return true;
}

int locate_index(int index)
{
    Node* p = vHead;
    // 定位到index的前一个
    while(p != nullptr && index--)
    {
        p = p -> next;
    }
    
    if(p == nullptr) return 0x3f3f3f3f;
    return p -> data;
}

void print_linked_list()
{
    
    Node* p = vHead -> next;
    if(p == nullptr) {cout << "Link list is empty" << endl; return;}
    while(p != nullptr && p -> next != nullptr)
    {
        cout << p -> data << " ";
        p = p -> next;
    }
    cout << p -> data << endl;
}

int main()
{
    int n; cin >> n;
    while(n--)
    {
        int t; cin >> t;
        insert_head(t);
    }
    int m; cin >> m;
    while(m--)
    {
        string f ; int op1 , op2;
        cin >> f;
        if(f == "show")
            print_linked_list();
        else if(f == "get")
        {
            scanf("%d" , &op1);
            int res = locate_index(op1);
            if(res == 0x3f3f3f3f) cout << "get fail" << endl;
            else cout << res << endl;
        }
        else if(f == "delete")
        {
            scanf("%d" , &op1);
            bool res = delete_index(op1);
            if(res) cout << "delete OK" << endl;
            else cout << "delete fail" << endl; 
        }
        else
        {
            scanf("%d %d" , &op1 , &op2);
            bool res = insert_index(op1 , op2);
            if(res) cout << "insert OK" << endl;
            else cout << "insert fail" << endl;
        }
    }
}
```

**解法二**

```c++
#include<iostream>
#include<string>
using namespace std;

const int N = 1e5; // 规定了链表可用的空间数量
// head 表示一个链表的头结点在 e数组中的位置 
// e[head] 是 head的值 对应结构体中的 head -> data
// ne[head] 是 head -> next 在 e中的位置。
// 可以类推 e 数组存储了 每个节点的数据 而 ne数组存储了 下一节点的位置
// head = -1 意味着 head -> next = nullptr 当 ne[i] = -1 代表访问到了链表最后一个位置。
int e[N] , ne[N] , head = -1 , idx = 1; 

// 头插法
void insert_head(int x)
{
    e[idx] = x; 
    ne[idx] = head;
    head = idx++;
}

int locate_index(int index)
{
    int p = head;
    while(p != -1 && --index)
        p = ne[p];

    if (p == -1) return 0x3f3f3f3f;
    return e[p];    
}

bool delete_index(int index)
{
    int p = head;
    if(head < 1) return false;
    if(index == 1)
    {
        head = ne[head];
        return true;
    }
    
    index--; 
    while(ne[p] != -1 && --index)
    {
        p = ne[p];      
    }
    
    if(ne[p] == -1) return false;
    else
    {
        ne[p] = ne[ne[p]];
        return true;
    }       
}

bool insert_index(int index , int a)
{
    if(index < 1) return false;
    if(index == 1) {insert_head(a); return true;}
    
    int p = head; index--;
    while(p != -1 && --index)
        p = ne[p];

    if(p == -1 || ne[p] == -1) return false;
    
    e[idx] = a;
    ne[idx] = ne[p];
    ne[p] = idx++;
    return true;
}

void print_linked_list()
{
    if(head == -1) 
    {
        cout << "Link list is empty" << endl;
        return;
    }

    int p = head;
    while(ne[p] != -1)
    {
        cout << e[p] << " ";
        p = ne[p];
    }
    cout << e[p] << endl;
}

int main()
{
    int n; cin >> n;
    while(n--)
    {
        int t; cin >> t;
        insert_head(t);
    }
    int m; cin >> m;
    while(m--)
    {
        string f ; int op1 , op2;
        cin >> f;
        if(f == "show")
            print_linked_list();
        else if(f == "get")
        {
            scanf("%d" , &op1);
            int res = locate_index(op1);
            if(res == 0x3f3f3f3f) cout << "get fail" << endl;
            else cout << res << endl;
        }
        else if(f == "delete")
        {
            scanf("%d" , &op1);
            bool res = delete_index(op1);
            if(res) cout << "delete OK" << endl;
            else cout << "delete fail" << endl; 
        }
        else
        {
            scanf("%d %d" , &op1 , &op2);
            bool res = insert_index(op1 , op2);
            if(res) cout << "insert OK" << endl;
            else cout << "insert fail" << endl;
        }
    }
}
```
