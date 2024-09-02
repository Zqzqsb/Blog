---
title: Form-Data
createTime: 2024-8-26
author: ZQ
tags:
  - web
permalink: /network/webserver/formdata/
---

## 概述

`form-data` 是一种用于发送表单数据到服务器的格式，通常在通过 `HTTP POST` 请求提交表单时使用。它允许在请求体中包含文本字段、文件等多种数据类型。`form-data` 格式的历史可以追溯到早期的 Web 开发，随着 Web 应用程序的复杂性增加，对表单数据的处理需求也不断增长。

## 背景

- **早期 Web 表单**：在最初的 Web 应用中，表单数据通常以 URL 编码的方式发送，即使用 `application/x-www-form-urlencoded` 格式。这种格式适合简单的键值对数据，但在处理文件上传时就显得不够灵活。
- - **引入 multipart/form-data**：为了支持文件上传和更复杂的表单数据，`multipart/form-data` 格式被引入。这种格式允许将数据分成多个部分，每个部分可以包含不同类型的数据（如文本、文件等），并且每个部分都有自己的内容类型。
- - **现代应用**：随着现代 Web 应用程序的发展，`form-data` 格式在 API 调用、文件上传和数据传输中变得越来越重要。许多库和框架（如 Axios、jQuery）都提供了对 `form-data` 的支持，使得开发者可以更方便地处理复杂的表单数据。


## 早期`web`

在最初的 Web 开发中，表单数据通常使用 `application/x-www-form-urlencoded` 格式发送。这种格式简单，但只能处理文本数据，且不支持文件上传。

**需求**：

- 提交简单的键值对数据

### 示例

**表单**

```html
<form action="/submit" method="POST">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Submit</button>
</form>
```

**URL编码**

```http
/submit?username=JohnDoe&password=mypassword
```

**服务端处理**

```javascript
const express = require('express');
const app = express();
app.use(express.urlencoded({ extended: true })); // 解析 URL 编码的请求体

app.post('/submit', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    res.send(`Received: ${username}, ${password}`);
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

### 局限

+ 无法很好的应对文件场景
+ 受到`URL`字符上限(Get场景), `maxRequestBody`(Post场景), `HTTP Header`长度(服务器)的限制

## `multipart/form-data`

随着 Web 应用程序的发展，文件上传的需求变得日益重要。`multipart/form-data` 格式被引入，以支持文本和文件的同时上传。

**需求**：

- 提交包含文件的表单数据。

### 构造请求

#### 请求头

- 请求头中的 `Content-Type` 标头指定了请求体的类型为 `multipart/form-data`，并包含了边界字符串（boundary string），用于分隔不同部分。
- 边界字符串是一个随机生成的字符串，用于标识每个部分的开始和结束。

```http
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
```

#### 请求体

- 请求体由多个部分组成，每个部分都以边界字符串开始，并以 `--` 结束。每个部分包含一个数据字段（如文本字段、文件等）。
- 每个部分包含以下内容：
    - `Content-Disposition` 标头，指定了字段的名称和可选的文件名。
    - 其他可选的标头，如 `Content-Type`（用于文件类型）、`Content-Length` 等。
    - 最后是字段的数据。

请求体示例：

```txt
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="username"

JohnDoe
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="example.jpg"
Content-Type: image/jpeg

(二进制文件数据)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

### 服务端处理

```javascript
const express = require('express');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' }); // 文件存储路径
const app = express();

app.post('/upload', upload.single('file'), (req, res) => {
    const username = req.body.username;
    const file = req.file;
    res.send(`Received: ${username}, File: ${file.originalname}`);
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

### 弊端

在早期的`web`开发实践中，这些信息往往是手动构造的。

## `FormData` API 和 `AJAX`

随着 Web 开发技术的进步，W3C 于 2010 年左右引入了 `FormData` API。这个 API 提供了一种更简便的方式来构造和管理表单数据，尤其是在处理 `multipart/form-data` 格式时。

1. **简化开发**：
    - 使用 `FormData` API，开发者可以通过简单的 `append()` 方法向 `FormData` 对象添加字段和文件，而不需要手动管理请求体的格式。
    - `FormData` 还自动处理边界字符串和 `Content-Type`，减少了出错的机会。
2. **现代开发的普及**：
    - 现代浏览器普遍支持 `FormData` API，使得它成为处理表单数据的标准方式。
    - 几乎所有现代 Web 应用程序都使用 `FormData` API 来处理表单提交，尤其是在需要上传文件的场景。

### 使用

```javascript
const formData = new FormData();
formData.append('username', 'JohnDoe');
formData.append('file', fileInputElement.files[0]);

fetch('https://example.com/upload', {
    method: 'POST',
    body: formData // 自动设置 Content-Type
});
```

### 总结 `FormData`

- `multipart/form-data` 是一种数据格式，定义了如何在 HTTP 请求中以多部分形式发送数据，而 `FormData` 是一个 JavaScript API，提供了更简便的方式来构造和管理这些数据。
- `FormData` API 自动处理了 `multipart/form-data` 的复杂性，使开发者能够更专注于应用逻辑，而不必过多关注底层的请求构造细节。