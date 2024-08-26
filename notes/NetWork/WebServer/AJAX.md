---
title: AJAX
createTime: 2024-8-26
author: ZQ
tag:
- web
---

## 简介

`AJAX`  全称为 Asynchronous Javascript and Xml.  其指代的是前端页面更新资源的一种方式， 它组合了：

- 浏览器内建的 `XMLHttpRequest` 对象（从 web 服务器请求数据）
- `JavaScript` 和 `HTML DOM`（显示或使用数据）

`Ajax` 是一个令人误导的名称。`Ajax` 应用程序可能使用 `XML` 来传输数据，但将数据作为纯文本或 `JSON` 文本传输也同样常见。

`Ajax` 允许通过与场景后面的 Web 服务器交换数据来异步更新网页。这意味着可以更新网页的
部分，而不需要重新加载整个页面。

## `XMLHttpRequest`

### 概述

`XMLHttpRequest` 是一个 JavaScript 对象，用于在网页与服务器之间进行异步通信。它使开发人员能够在不重新加载整个页面的情况下，从服务器请求数据并更新网页的部分内容。这种技术被广泛用于实现 AJAX（Asynchronous JavaScript and XML）功能。

### 主要特点

1. **异步请求**：`XMLHttpRequest` 允许发送异步请求，这意味着用户可以继续与页面交互，而不必等待服务器响应。
2. **支持多种数据格式**：尽管名称中包含 "XML"，`XMLHttpRequest` 也支持 JSON、HTML 和纯文本等多种数据格式。
3. **跨域请求**：通过设置适当的 CORS（跨源资源共享）头部，`XMLHttpRequest` 可以进行跨域请求。

### 用法示例

#### 使用回调函数

```javascript
var xhr = new XMLHttpRequest(); // 创建 XMLHttpRequest 对象
xhr.open("GET", "https://api.example.com/data", true); // 初始化请求

// 异步回调函数
xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) { // 请求完成
        if (xhr.status === 200) { // 请求成功
            console.log(xhr.responseText); // 处理响应数据
        } else {
            console.error("请求失败，状态码：" + xhr.status);
        }
    }
};

xhr.send(); // 发送请求
```

#### 使用`promise`

```javascript
function fetchData(url) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    resolve(xhr.responseText); // 请求成功，调用 resolve
                } else {
                    reject("请求失败，状态码：" + xhr.status); // 请求失败，调用 reject
                }
            }
        };
        xhr.send();
    });
}

// 使用 Promise
fetchData("https://api.example.com/data")
    .then(function (data) {
        console.log(data); // 处理成功的响应
    })
    .catch(function (error) {
        console.error(error); // 处理错误
    });
```

## `AJAX`工作原理

![AJAX pipeline](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/WEB/AJAX/AJAXPipeline.png)

### 解读

1. 网页中发生一个事件（页面加载、按钮点击）
2. 由 JavaScript 创建 XMLHttpRequest 对象
3. XMLHttpRequest 对象向 web 服务器发送请求
4. 服务器处理该请求
5. 服务器将响应发送回网页
6. 由 JavaScript 读取响应
7. 由 JavaScript 执行正确的动作（比如更新页面）

## `Axios`

`axio` 是一个流行的基于 `Promise` 的 `HTTP` 客户端，用于在浏览器和 `Node.js` 中发起 `HTTP` 请求。`axios` 可以用于替代传统的 `XMLHttpRequest` 对象，简化了异步请求的处理，并提供了更清晰、更易用的 API。在现代web开发多使用`Axios`

### 和`AJAX`的关系

- `AJAX` 是一种技术，用于在网页上实现异步通信，从而实现动态更新页面内容。
- `axios` 是一个 `JavaScript` 库，用于发起 `HTTP` 请求，支持 `PromiseAPI`，使得处理异步请求更加简单和直观。
- `axios` 可以被用来实现 `AJAX` 功能，但它提供了更加现代化和易用的接口。

### 使用

#### 基本使用

```javascript
// 引入 axios
import axios from 'axios';

// 发起 GET 请求
axios.get('https://api.example.com/data')
    .then(response => {
        console.log(response.data); // 处理成功的响应数据
    })
    .catch(error => {
        console.error(error); // 处理错误
    });
    
// 发起 POST 请求
axios.post('https://api.example.com/data', { key: 'value' })
    .then(response => {
        console.log(response.data); // 处理成功的响应数据
    })
    .catch(error => {
        console.error(error); // 处理错误
    });
```

对比上一节可以看出，`axios`使用`promise`实现了对`XMLHttpRequest`的封装。

#### 拦截器

`axios` 提供了拦截器功能，可以在请求或响应被处理前拦截它们。

```javascript
// 请求拦截器
axios.interceptors.request.use(config => {
    // 在请求发送之前做些什么
    return config;
}, error => {
    // 对请求错误做些什么
    return Promise.reject(error);
});

// 响应拦截器
axios.interceptors.response.use(response => {
    // 对响应数据做些什么
    return response;
}, error => {
    // 对响应错误做些什么
    return Promise.reject(error);
});
```

### 其他功能

`axios` 还支持取消请求、设置请求超时、传递请求头信息等功能，使得处理 HTTP 请求变得更加灵活和可靠。

