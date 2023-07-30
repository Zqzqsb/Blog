---
title: JavaScript Array
categories: JavaScript
date: "2022-7-11"
cover: "js_array.jpg"
description: "本文参照MDN文档对js中的数组做出了解释"
---

# JS array

## Construt

+ 以已有值构建数组

```javascript
const element0 = 0 , element1 = 1 , elementN = 'N';
const arr1 = new Array(element0, element1, /* … ,*/ elementN);
const arr2 = Array(element0, element1, /* … ,*/ elementN);
const arr3 = [element0, element1, /* … ,*/ elementN];

console.log(arr1 , arr2 , arr3);
console.log(arr1.prototype , arr2.prototype , arr3.prototype);

// output : [ 0, 1, 'N' ] [ 0, 1, 'N' ] [ 0, 1, 'N' ]
// output : undefined undefined undefined
```

**可以看到 这三种方式构建出的数组没有什么区别**

+ 单参数构造函数

```javascript
const arr1 = new Array(5);
console.log(arr1 , arr1[0] , arr1.prototype);
// output : [ <5 empty items> ] undefined undefined

const arr2 = Array(5);
console.log(arr2 , arr2[0] , arr2.prototype);
// output : [ <5 empty items> ] undefined undefined
```

+ 解释器不会进行构造函数匹配

```js
const arr = Array(9.3); // RangeError: Invalid array length
```

这段可以解释为创建单个元素的数组，但是js解释器没有采用这种工作方式。(或许是为消除歧义)

为了实现这种方式，可以采用Array.of()。

```js
const wisenArray = Array.of(9.3); // wisenArray 只包含一个元素：9.3
```

## length

+ length的字面含义  length标志了数组的使用状态，包括所有有效元素，空槽，和undefined。

+ 要注意以下几点

  + 数组继承自原型链中的对象，其下标索引对应的是普通属性，同时也会含有一些属性，而length只标志所有普通属性的数量。

    ```js
     // 一个含两个空槽，一个未定元素和一个普通元素的数组
    const arr4 = [ , undefined , , 1 ];
    console.log(arr4.length);
    arr4[3.5] = 1;
    console.log(arr4.length ,arr4);
    // output : 3 [ <1 empty item>, undefined, <1 empty item>, '3.5': 1 ]
    ```

  + 数组可以越界访问，赋值，这些操作会导致数组内部元素和属性的变化。

    ```js
    const arr3 = [];
    console.log(arr3 , arr3[0] , arr3.prototype); // 这是一个越界的访问
    // output : [] undefined undefined
    
    // 直接修改length的值 会向目标的长度开辟空槽
    arr3.length = 5; 
    console.log(arr3 , arr3[0] , arr3.prototype);
    // output : [ <5 empty items> ] undefined undefined
    
    // 空槽仍会保留在数组中 length随着元素的加入而增加
    for(i = 1 ; i <= 6 ; i++)
        arr3.push(i);
    console.log(arr3 , arr3.length)
    // output : [ <5 empty items>, 1, 2, 3, 4, 5, 6 ] 11
    
    // 删除元素会形成空槽
    delete arr3[10];
    console.log(arr3 , arr3.length);
    // [ <5 empty items>, 1, 2, 3, 4, 5, <1 empty item> ] 11
    ```

  + 而改变length的长度会使array发生尾部截断。这是一个不可逆的过程。

    ```js
    arr3.length = 7;
    console.log(arr3)
    // output : [ <5 empty items>, 1, 2 ]
    arr3.length = 11;
    console.log(arr3);
    // output : [ <5 empty items>, 1, 2, <4 empty items> ]
    ```

+ 注意: 空槽和undefined的内存管理取决于解释器。可以确定的是，解释器一定会为undefined属性开辟内存，而空槽则不一定。

## Reference

正是上文提到的数组length及相关特性，可以对数组进行间隔(甚至是越界)填充。

```js
const arr1 = Array(10);
arr1[0] = 1, arr1[20] = 1;
console.log(arr1 , arr1.length);
// [ 1, <19 empty items>, 1 ] 21
```

 事实上，初始化的length没有在这一过程中决定任何事情。

+ 有效元素

  ```js
  // filter的原型定义在 Array.prototype.filter()中
  const arr1_valid = arr1.filter(elem => elem !== undefined);
  console.log(arr1 , arr1_valid);
  // output : [ 1, <19 empty items>, 1 ] [ 1, 1 ]
  ```

如果填充了一个非整数位置。那么将视为设置array对象的属性

```js
arr1[7.8] = 'A';
console.log(arr1);
// [ 1, <19 empty items>, 1, '7.8': 'A' ]
```

## Traverse

+ 传统的遍历方法

  ```js
  const colors = ["red", "green", "blue"];
  for (let i = 0; i < colors.length; i++) {
    console.log(colors[i]);
  }
  ```

+ 访问类数组(array-liked object)对象

  ```js
  // divs不支持push() , pop()等操作
  // 这里事实上有两个思想 1.数组的过滤 2.div = divs[i]是个迭代的过程，当i越界时会返回否
  const divs = document.getElementsByTagName("div");
  for (let i = 0, div; (div = divs[i]); i++) {
    /* 以某种方式处理 div */
  }
  ```

  迭代过程中的false和undefined

  ```js
  const arr1 = [1 , 2 , false , 3 , 4];
  for(let i = 0 , elem ; elem = arr1[i] ; i++)
      console.log(arr1[i]);
  // 1 2
  arr1[2] = undefined;
  for(let i = 0 , elem ; elem = arr1[i] ; i++)
      console.log(arr1[i]);
  // 1 2
  arr1[2] = 'a';
  for(let i = 0 , elem ; elem = arr1[i] ; i++)
      console.log(arr1[i]);
  // 1 2 3 4 5 
  ```

+ ForEach()

  ```js
  const colors = ['red', 'green', 'blue']; 
  colors.forEach((color) => console.log(color)); // 匿名函数
  // red
  // green
  // blue
  ```

  非手动定义的undefined在ForEach遍历不会被列出

  ```js
  const sparseArray = ['first', 'second', , 'fourth'];
  
  sparseArray.forEach((element) => {
    console.log(element);
  });
  // first
  // second
  // fourth
  
  if (sparseArray[2] === undefined) {
    console.log('sparseArray[2] 是 undefined');  // true
  }
  
  const nonsparseArray = ['first', 'second', undefined, 'fourth'];
  
  nonsparseArray.forEach((element) => {
    console.log(element);
  });
  // first
  // second
  // undefined
  // fourth
  
  ```

  如果采用for...in 遍历，会的得到所有数组的所有普通元素和可枚举属性。

  ```js
  arr1['proc1'] = 'a_proc';
  for (let proc in arr1)
      console.log(arr1[proc]);
  // 1 2 a 3 4 a_proc
  ```

+ for of (ES6) 列出元素会含undefined

  ```js
  console.log();
  arr1.length = 6;
  console.log(arr1);
  for (elem of arr1)
      console.log(elem);
  // [ 1, 2, 'a', 3, 4, <1 empty item>, proc1: 'a_proc' ]
  // 1
  // 2
  // a
  // 3
  // 4
  // undefined
  ```

  ## methods

+ contact(some_arr) 连接两个或多个数组并返回新数组

  + ```js
    let myArray = ['1', '2', '3'];
    myArray = myArray.concat('a', 'b', 'c');
    // myArray 现在是 ["1", "2", "3", "a", "b", "c"]
    
    ```

+ join(str) 将数组所有元素以某个分割符链接为字符串

  + ```js
    const myArray = ['Wind', 'Rain', 'Fire'];
    const list = myArray.join(' - '); // list 现在是 "Wind - Rain - Fire"
    ```

+ push(elem) 在数组末尾添加一个或多个元素，返回数组length

  + ```js
    const myArray = ['1', '2'];
    myArray.push('3'); // myArray 现在是 ["1", "2", "3"]
    ```

+ pop() 移除并返回数组的最后一个元素

  + ```js
    const myArray = ['1', '2', '3'];
    const last = myArray.pop();
    // myArray 现在是 ["1", "2"]，last 为 "3"
    ```

+ shift() 移出并返回第一个元素

  + ```js
    const myArray = ['1', '2', '3'];
    const first = myArray.shift();
    // myArray 现在是 ["2", "3"]，first 为 "1"
    ```

+ unshift(elem) 在数组头部添加一个元素， 返回length

  + ```js
    const myArray = ['1', '2', '3'];
    myArray.unshift('4', '5');
    // myArray 变成了 ["4", "5", "1", "2", "3"]
    ```

+ slice(a,b) 左闭右开

  + ```js
    let myArray = ["a", "b", "c", "d", "e"];
    myArray = myArray.slice(1, 4); // [ "b", "c", "d"]
    // 从索引 1 开始，提取所有的元素，直到索引 3 为止
    ```

+ at(index) 用于取负下标

  + ```js
    const myArray = ['a', 'b', 'c', 'd', 'e'];
    myArray.at(-2); // "d"，myArray 的倒数第二个元素
    ```

+ splice(a , b , e1 , e2 , .... , en) 删除a，b段的元素 并且将后续元素ei 接在删除位置之后

  + ```js
    const myArray = ['1', '2', '3', '4', '5'];
    myArray.splice(1, 3, 'a', 'b', 'c', 'd');
    // myArray 现在是 ["1", "a", "b", "c", "d", "5"]
    // 本代码从 1 号索引开始（或元素“2”所在的位置），
    // 移除 3 个元素，然后将后续元素插入到那个位置上。
    ```

+ reverse() 逆序

+ flat() 展平

+ sort(cmp(a , b) 排序

  + 可以接受一个回调函数作为参数

+ indexof(elem)

  + 返回第一个匹配的索引

+ lastIndexof(elem)

  + 反向搜索 返回第一个匹配的索引

+ forEach(elem => op)

  + 对每函数执行r回调函数
  + 会使用for...of进行属性检查

+ reduce((acc , curV , curI , arr) => {op} , initV)

  + reduce接受一个回调函数这个回调函数会从数组的第一个位置开始执行直到数组的最后一个位置
    + 对于这个函数的参数 acc指定的累加器的当前值 curV是数组当前值 curI是数组当前下标 arr是这个数组本身
    + 如果只需要传递部分内容 例如只关心累加器和当前元素下标 应这样进行参数传递(acc , _ , curl) 即间隔的位置的参数不可以省略
    + initV规定额acc的初始值

  + 这个函数的返回结果会作为reduce的最终返回结果
















