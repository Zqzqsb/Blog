Title: Web_VerifyCode
categoryies: web
date: "2023-7-13"
cover: "封面.png"
description:
  "该博客对50projects50days中的第一个项目做出了详解"

# verify code

## 前言

本文旨在阐述一个最基本的web项目是如何工作的，并尝试理解其中的各种代码细节。

## 源码的直观解读

+ html 部分

  + 在html头部规定了html文件的属性信息，包括语言，字符集，页面标题 相关联的css样式文件等

    ```html
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <link rel="stylesheet" href="style.css" />
        <title>Verify Account</title>
      </head>
    ```

  + 接着是body部分

    + body包含一个container 其中除了一些提示信息 最重要的是一个自定子元素 code-contiainer
      + 可以在css中查看code-contianer的样式信息
    + code-contianer包含六个code元素 每个code同样是自定样式元素 同时它也是一个html表单控件

    ```html
      <body>
        <div class="container">
          <h1>Verify Your Account</h1>
          <p>We emailed you the six digit code to cool_guy@email.com <br/> Enter the code below to confirm your email address.</p>
          <div class="code-container">
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
            <input type="number" class="code" placeholder="0" min="0" max="9" required>
          </div>
          <small class="info">
            This is design only. We didn't actually send you an email as we don't have your email, right?
          </small>
      </body>
      <script src="script.js"></script>
    </html>
    ```

  + 页面效果

    ![页面效果](页面效果.png)

+ js 部分

  + js文件约定了网页元素和用户操作的交互方式

    ```js
    const codes = document.querySelectorAll(".code");
    codes[0].focus();
    codes.forEach((code, idx) => {
        code.addEventListener("keydown", (e) => {
            if (e.key >= 0 && e.key <= 9) {
            	codes[idx].value = "";
                if(idx !== 5) setTimeout(() => codes[idx + 1].focus(), 10);
            } else if (e.key === "Backspace") {
                if(idx !== 0) setTimeout(() => codes[idx - 1].focus(), 10);
            }
        });
    })
    ```

  + 首先从document对象中利用css类选择器选出所有的code对象 并放回一个对象列表codes

  + 将焦点设置在codes的第一个元素上

  + forEach使用迭代的方式为每个code元素增加一个事件监听器 该监听器每次清空这个code以**迎接**用户的输入,该功能保证了一个node中只会有一个输入，并且焦点会随着用户的输入和删除而移动

    + 事件监听器只会监听作用在持有该监听器的那个code元素的动作。即如果code1的事件监听器只会监听作用在code1上的keydown事件。

+ 

