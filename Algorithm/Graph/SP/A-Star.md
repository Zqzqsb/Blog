---
title: A-Star
categories:
  - 算法
tags:
  - 图论
  - 最短路
createTime: 2024-10-24
permalink: /algorithm/graph/astar/
---
![A-Star](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/A-Star/A-Star.gif)

`A-Star`加入了启发式函数，使得路径搜索更为高效。本文讲解了`A-Star`算法的一些细节。

<!-- more -->

## 概述

`A-Star`的诉求是通过一定的启发式条件剪枝掉一定的搜索空间。考虑在二维网格中搜索两个点的最短路径。如果使用宽搜类算法，其搜索路径如图所示。

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/A-Star/BfsDemo.gif)

可以想见的是，如果在搜索过程加上终点位置这一信息之后，每个搜索点的位置就不再**平等**，距离终点的终点距离更近的点成为了更好的点，如果可以优先搜索这些点，那么可以更快的搜索到终点。

基于这样的思想`A-Star`算法便诞生了。观察其搜索路径图示。

![A-Star](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/A-Star/A-Star.gif)

## 估计函数

考虑这样细节:
+ 因为障碍的存在，我们不能准确估计哪些点是搜索终点更近的
	+ 视觉上更近的点在搜索路劲中可能更远

正如这一节的标题，对于距离搜索终点的距离是一种估计。
### 估价的细节

**估价函数有这样一些要求**

1.  搜索目标点必须是存在，换言之，这个搜索过程必须是有解的。
2. 估价函数的取值范围需要满足该不等式 
	+ 真实值 >= 估计值 >= 0
3. 估价函数需要反应真实的单调性常见的估价函数设计思路
	+ 基于距离 比如曼哈顿距离 欧式距离 对角距离
	+ 基于真实的最短距离

## 算法过程

+ 同时计算当前的搜索距离(成本)`D`和距离终点的估价距离`F`。这二者的和反应了路径的估计总成本。
+ 维护一个优先队列，每次弹出路径估计总成本最低的节点出队，更新其他节点的距离。
+ 当搜索终点第一次出队时，结束搜索，这时的路径为最短路径。

## 相关证明

### 正确性

**证** : 第一次搜索到终点为最优路径。

+ 假设第一次搜索到终点`e`不为最优，那么现在搜索路径中存在某个待选点 `w` , 经过`w`的路径是最优的真实路径。
	+ 则 `D(e) + F(e) >= real(d) >= D(w) + F(w)`
+ 那么便推出了矛盾，`w`应该先于`e`出队

### 图解

考虑这样的情况

![](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Algorithm/A-Star/Demo.png)
路径会在框示节点回溯，从起点的右侧节点开始重新更新底侧路径的搜索距离。

> 对于其他节点，第一次搜索到并不一定是最小的。
> 终点搜索正确性是由估价函数的取值范围来保证的。

## 例题

> [Acwing 179 八数码](https://www.acwing.com/problem/content/description/181/)

```cpp
#include<iostream>
#include<map>
#include<queue>
#include<string>
#include<map>
#include<algorithm>
#include<utility>

using namespace std;
typedef pair<int , string> PII;

// 由于每次只移动一个节点 所以可以使用曼哈顿距离来进行估价
int cal(string state)
{
    int res = 0;
    for (int i = 0; i < state.size(); i ++ )
        if (state[i] != 'x')
        {
            int t = state[i] - '1';
            res += abs(i / 3 - t / 3) + abs(i % 3 - t % 3);
        }
    return res;
}

string Astar(string start)
{
    priority_queue<PII , vector<PII> , greater<PII>> q;
    unordered_map<string , pair<string , char>> prev;
    unordered_map<string , int> dist;
    string end = "12345678x";
    q.push({cal(start) + 0 , start}); dist[start] = 0;
    
    int tx[] = { 0 , 0 , 1 , -1 };
    int ty[] = { 1 , -1 , 0 , 0 };
    string ops = "rldu";
    
    while(q.size())
    {
        PII f = q.top(); q.pop();
        string state = f.second; int step = f.first;
        
        if(state == end) break; 
        
        int idx = state.find('x');
        int x = idx / 3 , y = idx % 3;
        
        string source = state;
        for(int i = 0 ; i <= 3 ; i++)
        {
            int nx  = x + tx[i] , ny = y + ty[i] , nidx = nx * 3 + ny;
            if(nx >= 0 && nx <= 2 && ny >= 0 && ny <= 2)
            {
                swap(state[idx] , state[nidx]);
                if(dist.count(state) == 0 || dist[state] > step + 1)
                {
                    dist[state] = step + 1;
                    prev[state] = { source , ops[i] };
                    q.push({dist[state] + cal(state) , state});
                }
                swap(state[idx] , state[nidx]);
            }
            
        }
    }
    
    string res = "";
    while(end != start)
    {
        res += prev[end].second;
        end = prev[end].first;
    }
    reverse(res.begin() , res.end());
    return res;
}


int main()
{
    string start , seq;
    char c;
    
    while(cin >> c)
    {
        start += c;
        if(c != 'x') seq += c;
    }
    
    int cnt = 0;
    for(int i = 0 ; i < 8 ; i++)
        for(int j = i ; j < 8 ; j++)
            if(seq[j] > seq[i]) cnt++;
    
    if(cnt % 2 == 1) {
        cout << "unsolvable";
        return 0;
    }
    
    cout << Astar(start);
}
```