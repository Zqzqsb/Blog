---
title: Asynchronous coding in javascript
createTime: 2024-4-11
tags:
  - JavaScript
  - 异步编程
author: ZQ
permalink: /javascript/asynchronous/
---

 本文记录了JavaScript异步编程中的一些细节。
 
<!-- more -->

##  单线程JavaScript

JavaScript 是单线程的。这意味着在任何给定的时间点，JavaScript 只能执行一个操作，不能并行处理多个任务。**主线程**用于浏览器处理用户事件和页面绘制等。默认情况下，浏览器在一个线程中运行一个页面中的所有 JavaScript 脚本，以及呈现布局，回流，和垃圾回收。这意味着一个长时间运行的 JavaScript 会阻塞线程，导致页面无法响应，造成不佳的用户体验。

尽管 JavaScript 是单线程的，但它仍然可以处理异步操作，如网络请求、定时器等。这是通过事件循环（Event Loop）和回调函数实现的。当一个异步操作（例如，一个网络请求）开始时，它会被发送到浏览器或 Node.js 的 API，这样 JavaScript 主线程可以继续执行其他操作。当异步操作完成时，它的回调函数会被放入一个任务队列（Task Queue）。事件循环不断地检查主线程是否空闲，如果空闲并且任务队列中有待处理的回调函数，就会将回调函数放到主线程中执行。

此外，JavaScript 在 ES6 中引入了 Promise，以及在 ES7 中引入了 `async/await`，这些新的特性都使得异步编程更加方便和直观。

尽管 JavaScript 是单线程的，但在某些情况下，你可以使用 Web Workers（在浏览器中）或 Worker threads（在 Node.js 中）来在后台线程上执行 JavaScript 代码，从而实现并行处理。但请注意，这些 Worker 线程并不共享主线程的内存，它们通过消息传递来进行通信。

##  基于Promise的异步模型 (ES6)

### 观察异步过程

样例
```javascript
const fetchPromise = fetch(
  "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",
);

console.log(fetchPromise);

fetchPromise.then((response) => {
  console.log(`已收到响应：${response.status}`);
});

console.log("已发送请求……");
```

```shell
Promise { <state>: "pending" }
已发送请求……
已收到响应：200
```

观察这个fetch过程，当`console.log(fetchPromise);` , fetch还处于pending状态。而发送请求先于收到响应被执行，即便在代码位置上它更靠后。

### 链式使用Promise

样例
```javascript
const fetchPromise = fetch(
  "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",
);

fetchPromise.then((response) => {
  const jsonPromise = response.json();
  jsonPromise.then((json) => {
    console.log(json[0].name);
  });
});
```

**json() 也是一个异步过程**

可以使用箭头函数简写。

```javascript
fetchPromise
	.then((response) => response.json())
	.then((json) => json.data)
	.error((e) => console.log('Error' , error))
```

这样形成的链式调用过程更加清晰，每个`Promise`的.then可以包裹一个异步的回调的函数并形成一个新的`Promise`。

### 合并使用Promise

有时你需要所有的 Promise 都得到实现，但它们并不相互依赖。在这种情况下，将它们一起启动然后在它们全部被兑现后得到通知会更有效率。这里需要 `Promise.all()`方法。它接收一个 Promise 数组，并返回一个单一的 Promise。

由`Promise.all()`返回的 Promise：

- 当且仅当数组中_所有_的 Promise 都被兑现时，才会通知 `then()` 处理函数并提供一个包含所有响应的数组，数组中响应的顺序与被传入 `all()` 的 Promise 的顺序相同。
- 会被拒绝——如果数组中有_任何一个_ Promise 被拒绝。此时，`catch()` 处理函数被调用，并提供被拒绝的 Promise 所抛出的错误。

```javascript
const fetchPromise1 = fetch("url1",);
const fetchPromise2 = fetch("url2",);
const fetchPromise3 = fetch("url3",);

Promise.all([fetchPromise1, fetchPromise2, fetchPromise3])
  .then((responses) => {
    for (const response of responses) {
      console.log(`${response.url}：${response.status}`);
    }
  })
  .catch((error) => {
    console.error(`获取失败：${error}`);
  });
```

除了all之外，还有更多的合并使用逻辑。

### Promise 术语

Promise 有三种状态：

- **待定（pending）**：初始状态，既没有被兑现，也没有被拒绝。这是调用 `fetch()` 返回 Promise 时的状态，此时请求还在进行中。
- **已兑现（fulfilled）**：意味着操作成功完成。当 Promise 完成时，它的 `then()` 处理函数被调用。
- **已拒绝（rejected）**：意味着操作失败。当一个 Promise 失败时，它的 `catch()` 处理函数被调用。

这里的“成功”或“失败”的含义取决于所使用的 API：例如，`fetch()` 认为服务器返回一个错误（如`404 Not Found`时请求成功，但如果网络错误阻止请求被发送，则认为请求失败。

有时我们用 **已敲定（settled）** 这个词来同时表示 **已兑现（fulfilled）** 和 **已拒绝（rejected）** 两种情况。

如果一个 Promise 处于已决议（resolved）状态，或者它被“锁定”以跟随另一个 Promise 的状态，那么它就是 **已兑现（fulfilled）**。

## 基于async 和 await的异步 (ES7)

### 概览

使用async定义异步函数。

```javascript
async function myFunction() {
  // 这是一个异步函数
}
```

在异步函数中，你可以在调用一个返回 Promise 的函数之前使用 `await` 关键字。这使得代码在该点上等待，直到 Promise 被完成，这时 Promise 的响应被当作返回值，或者被拒绝的响应被作为错误抛出。

在函数中，每一步会顺讯的执行，如果遇到需要待处理的promise，整个函数都将被挂起，将主线程交给其他程序。当线程控制权回到异步函数时，如果promise已经处理完成，那么便从函数挂起的位置继续执行。

这个过程就好像我们在编写一个同步函数一样。

```javascript
async function fetchProducts() {
  try {
    // 在这一行之后，我们的函数将等待 `fetch()` 调用完成
    // 调用 `fetch()` 将返回一个“响应”或抛出一个错误
    const response = await fetch(
      "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",
    );
    if (!response.ok) {
      throw new Error(`HTTP 请求错误：${response.status}`);
    }
    // 在这一行之后，我们的函数将等待 `response.json()` 的调用完成
    // `response.json()` 调用将返回 JSON 对象或抛出一个错误
    const json = await response.json();
    console.log(json[0].name);
  } catch (error) {
    console.error(`无法获取产品列表：${error}`);
  }
}

fetchProducts();
```

这里我们调用 `await fetch()`，我们的调用者得到的并不是 `Promise`，而是一个完整的 `Response` 对象。但请注意，这个写法只在异步函数中起作用，并且异步函数总是返回一个 Pomise。

```javascript
async function fetchProducts() {
  try {
    const response = await fetch(
      "https://mdn.github.io/learning-area/javascript/apis/fetching-data/can-store/products.json",
    );
    if (!response.ok) {
      throw new Error(`HTTP 请求错误：${response.status}`);
    }
    const json = await response.json();
    return json;
  } catch (error) {
    console.error(`无法获取产品列表：${error}`);
  }
}

const jsonPromise = fetchProducts();
jsonPromise.then((json) => console.log(json[0].name));
```

就像一个 Promise 链一样，`await` 强制异步操作以串联的方式完成。如果下一个操作的结果取决于上一个操作的结果，这是必要的，但如果不是这样，像 `Promise.all()` 这样的操作会有更好的性能。


### 总结

async 和 await 事实上对应promise链式使用的语法糖，他们的适用场景很相似。


## 基于Workers的异步

### 和promise的比较

Promise 和 Web Workers 都可以用于处理异步操作，避免阻塞 UI，但它们有一些本质不同。

1. 计算密集型任务：Promise 是异步处理 I/O（输入/输出）操作的一种方式，如网络请求或文件读写，这些操作通常会因等待响应或数据而导致阻塞。Promise 使得你能够在等待这些操作完成的同时去执行其他任务。但是，如果你有一项计算密集型任务，例如复杂的图像处理或大量数据的计算，即便你将它放在 Promise 中，它仍然会在主线程上运行，可能会阻塞 UI。这时，你可能需要使用 Web Workers，因为它们在后台线程上运行代码，不会影响到主线程和 UI。
2. 数据共享：Promise 在处理异步任务时，并不会创建新的执行上下文，这意味着你可以直接访问和修改主线程中的数据。然而，Web Workers 是在与主线程隔离的上下文中运行的，它们不能直接访问或修改主线程中的数据，必须通过消息传递的方式来交换数据。这对于处理大量数据的任务可能会更有效，因为你可以将数据传输到 Worker，让 Worker 在后台处理，然后再将结果传回主线程，这样可以避免阻塞主线程。
3. 错误处理：Promise 提供了一种结构化的错误处理机制，你可以在 Promise 链的末尾使用 `.catch` 方法来捕获所有的异步错误。然而，Web Workers 的错误处理需要通过监听 `error` 事件来实现，这可能会让错误处理变得更复杂。

###  Dedicated  Workers

workers事实上有三类。

- dedicated workers
- shared workers
- service workers

这里着重介绍一下第一种dedicated workers。

### 用worker进行质数生成

```vue
<template>
  <div>
    <input type="number" v-model="quota" placeholder="Enter a quota">
    <button @click="generatePrimes">Generate primes</button>
    <div>{{ output }}</div>
    <button @click="reloadPage">Reload Page</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const worker = new Worker(new URL('./generate.js', import.meta.url));
const quota = ref('');
const output = ref('');

const generatePrimes = () => {
  worker.postMessage({
    command: 'generate',
    quota: quota.value,
  });
};

worker.addEventListener('message', (message) => {
  output.value = `Finished generating ${message.data} primes!`;
});

const reloadPage = () => {
  location.reload();
};
</script>
```

上面是使用vue的单组件应用，下面是`generate.js`的内容，它们之间需要通过消息进行通信。

```javascript
// 监听主线程中的消息。
// 如果消息中的 command 是 "generate"，则调用 `generatePrimse()`
addEventListener("message", (message) => {
  if (message.data.command === "generate") {
    generatePrimes(message.data.quota);
  }
});

// 生成质数 (非常低效)
function generatePrimes(quota) {
  function isPrime(n) {
    for (let c = 2; c <= Math.sqrt(n); ++c) {
      if (n % c === 0) {
        return false;
      }
    }
    return true;
  }

  const primes = [];
  const maximum = 1000000;

  while (primes.length < quota) {
    const candidate = Math.floor(Math.random() * (maximum + 1));
    if (isPrime(candidate)) {
      primes.push(candidate);
    }
  }

  // 完成后给主线程发送一条包含我们生成的质数数量的消息消息。
  postMessage(primes.length);
}

```

只要主脚本创建 worker，这些代码就会运行。
