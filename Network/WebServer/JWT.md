---
title: JWT
createTime: 2025-1-28
author: ZQ
tags:
  - web
permalink: /network/webserver/jwt/
---

`JWT`实现了服务器侧的无状态，一种用于在网络应用场景中安全地传输声明的开放标准（RFC 7519）。它可以用于身份验证、授权信息传递或信息加密传输等场景。

<!-- more -->

## 基本结构

一个典型的 JWT 字符串用“`.`”分隔成三部分：

```
header.payload.signature
```

### **Header**：描述 JWT 的元数据，通常包含两部分信息：

1. 算法（`alg`）：签名或加密的算法，如 `HS256`（HMAC-SHA256）或 `RS256`（RSA-SHA256）。
2. 类型（`typ`）：通常为 `"JWT"`。

### **Payload**：实际的“声明”或“负载”数据，包含一系列键值对，例如用户ID、发行时间、过期时间等。

- **常见的标准字段**（RFC 7519 定义了部分字段）：
    - `iss` (Issuer): 签发者
    - `sub` (Subject): 面向的用户
    - `aud` (Audience): 接收方
    - `exp` (Expiration Time): 过期时间
    - `nbf` (Not Before): 在此时间之前不可用
    - `iat` (Issued At): 签发时间
    - `jti` (JWT ID): 唯一标识
- 也可以添加自定义字段（如 `user_id`, `role` 等）。

### **signature**：用于保证数据完整性，并验证 **Header** 和 **Payload** 未被篡改。

- 首先将 `header` 和 `payload` 分别进行 Base64URL 编码，然后按以下方式生成签名：

```
signature = HMAC-SHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret_key )
```

如果使用的是对称加密算法，如 HS256，就需要客户端和服务端使用同一个 `secret_key`。  
如果是非对称算法（如 RSA），会使用**私钥**进行签名、用**公钥**验证签名。

将这三部分用“`.`”拼接在一起，就构成了一个完整的 JWT 字符串，例如：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiIsImlhdCI6MTY3MDIxMTgxMiwiZXhwIjoxNjcwMjE1NDEyfQ
.4mfAAg77YRqHz9u7f1oyWR-Ar4qnGoxc6Moav8-jkCM
```

### 总结

`jwt`的信息部分是明文传输的，包含一个对于信息的校验码。

## 使用场景

###  身份验证

- 用户登录成功后，服务端生成一个带有用户信息（如 user_id, role 等）的 Token，返回给客户端。
- 客户端在后续请求中，通常把 Token 放在 `Authorization: Bearer <token>` 头里发送给服务端。
- 服务端通过验证签名和检查 `exp`（过期时间）等字段来确定 Token 是否有效，并解析出用户身份。

### 信息传输

- 有时 JWT 可用于安全地传递某些信息（比如在微服务之间），确保对方能验证数据真实性。
- 但要注意**JWT 一般不可随意存放敏感数据**，因为在没有额外加密情况下，任何人都可以解码（Base64URL 解码）看到 `payload` 内容；JWT 主要保证**完整性**，而非**机密性**。

### 分布式系统或无状态认证

- 使用 JWT，可以在服务端不保存会话状态（无需 Session），每次客户端都带上 Token，服务端只要验证 Token 是否正确并未过期即可。
- 减少了服务端维护 Session 的负担，适合分布式部署或微服务架构。

## 劣势

- **难以主动失效**
    
    - JWT 签发后，一般在到期前都是有效的，如果用户想要注销或服务器需要强制失效 Token，需要额外的策略，比如维护一个“黑名单”或在发行时引入可回收机制。
    
- **Payload 明文可读**
    
    - 标准 JWT 如果不做加密，任何人都可 Base64 解码查看 Payload，因此**不要**把敏感信息（如密码、银行信息等）直接放在 Token 里。
    
- **Token 一旦泄露**
    
    - 如果 Token 在未过期之前被攻击者获取，且没有办法主动失效，就会导致被盗用。

## 前端存储

- Web 前端通常把 Token 存在 `HTTP-Only Cookie` 或 `LocalStorage` 中，但前者更安全（可防止大多数 XSS 窃取）。

## 中间件实现

以 `hertz`的 `jwt` 中间件为例。

```go
package mw // 定义包名为 mw，通常用于存放中间件相关的代码

import (
	"context"
	"fmt"
	"net/http"
	"time"

	// 导入项目内部的包
	// 数据库访问层，用于检查用户信息
	"github.com/cloudwego/hertz/pkg/app"          // Hertz 框架的 app 包，处理请求上下文
	"github.com/cloudwego/hertz/pkg/common/hlog"  // Hertz 的日志包
	"github.com/cloudwego/hertz/pkg/common/utils" // Hertz 的工具包，包含辅助函数
	"github.com/cloudwego/hertz/pkg/protocol/consts"
	"github.com/hertz-contrib/jwt" // Hertz 的 JWT 中间件包
	"zqzqsb.com/gomall/app/user/biz/model"
	"zqzqsb.com/gomall/app/user/biz/service"
	"zqzqsb.com/gomall/app/user/kitex_gen/user"
)

// 全局变量，用于存储初始化后的 JWT 中间件实例
var (
	JwtMiddleware *jwt.HertzJWTMiddleware // JWT 中间件实例
	IdentityKey   = "identity"            // 用于在 JWT 载荷中存储用户身份的键
)

// InitJwt 初始化 JWT 中间件
func InitJwt() {
	var err error
	// 创建新的 JWT 中间件实例并配置相关参数
	JwtMiddleware, err = jwt.New(&jwt.HertzJWTMiddleware{
		Realm:         "test zone",                                        // 认证领域，用于在 WWW-Authenticate 头中返回
		Key:           []byte("secret key"),                               // 用于签名 JWT 的密钥，请确保使用足够复杂且安全的密钥
		Timeout:       time.Hour,                                          // JWT 的有效期，此处设置为 1 小时
		MaxRefresh:    time.Hour,                                          // 允许刷新 JWT 的最大时间，此处设置为 1 小时
		// 表示在解析请求时，会尝试从以下几处获取 Token：
		// HTTP Header 中的 Authorization 字段
		// URL 查询参数 ?token=xxx
		// Cookie 名为 jwt
		// （按照这个顺序依次查找）
		TokenLookup:   "header: Authorization, query: token, cookie: jwt", // 定义从哪里查找 JWT
		TokenHeadName: "Bearer",                                           // JWT 在请求头中的前缀
		// 自定义登录成功后的响应格式
		LoginResponse: func(ctx context.Context, c *app.RequestContext, code int, token string, expire time.Time) {
			// 直接set一个http only cookie 给客户端
			c.SetCookie(
				"jwt", // Cookie名称
				token, // Cookie值
				3600,  // 过期时间(秒)
				"/",   // 路径
				"",    // 域名(留空表示当前域)
				protocol.CookieSameSiteDefaultMode,
				true, // Secure
				true, // HttpOnly
			)
			c.JSON(http.StatusOK, utils.H{
				"code":    code,                        // 状态码
				"token":   token,                       // 生成的 JWT Token
				"expire":  expire.Format(time.RFC3339), // 过期时间
				"message": "success",
			})
		},
		// 认证函数，用于验证用户登录信息
		Authenticator: func(ctx context.Context, c *app.RequestContext) (interface{}, error) {
			var err error
			var req user.LoginReq
			err = c.BindAndValidate(&req)
			if err != nil {
				c.String(consts.StatusBadRequest, err.Error())
				return nil, err
			}
			LoginService := service.NewLoginService(ctx)
			resp, err := LoginService.Run(&req)
			if err != nil {
				c.String(consts.StatusInternalServerError, fmt.Sprintf("Registration failed: %v", err))
				return nil, err
			}
			return resp.UserId, nil
		},
		IdentityKey: IdentityKey, // 设置用于标识用户身份的键
		// 从 JWT 载荷中提取用户身份信息
		IdentityHandler: func(ctx context.Context, c *app.RequestContext) interface{} {
			claims := jwt.ExtractClaims(ctx, c) // 提取 JWT 载荷中的声明
			return &model.User{
				ID: claims[IdentityKey].(uint), // 使用声明中的身份键获取用户ID
			}
		},
		// 将用户数据转换为 JWT 载荷中的声明
		PayloadFunc: func(data interface{}) jwt.MapClaims {
			if v, ok := data.(*model.User); ok {
				return jwt.MapClaims{
					IdentityKey: v.ID, // 将用户ID存储在 JWT 载荷中
				}
			}
			return jwt.MapClaims{} // 返回空的声明
		},
		// 自定义 HTTP 状态消息函数，用于记录错误日志并返回错误消息
		HTTPStatusMessageFunc: func(e error, ctx context.Context, c *app.RequestContext) string {
			hlog.CtxErrorf(ctx, "jwt biz err = %+v", e.Error()) // 记录错误日志
			return e.Error()                                    // 返回错误消息
		},
		// 自定义未授权响应
		Unauthorized: func(ctx context.Context, c *app.RequestContext, code int, message string) {
			c.JSON(http.StatusOK, utils.H{
				"code":    code,    // 状态码
				"message": message, // 错误消息
			})
		},
	})
	// 如果初始化过程中出现错误，程序将崩溃并输出错误信息
	if err != nil {
		panic(err)
	}
}
```
