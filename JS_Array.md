---
title: JavaScript Array
categories: JavaScript
date: "2022-7-11"
cover: "封面.png"
description: "本文参照MDN文档对js中的数组做出了解释"
---



# JS array

## Construct

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

+ 从可迭代对象中构造数组

  ```js
  var str = "123"; //String is iterable
  const arr4 = Array.from(str); //['1','2','3']
  console.log(arr4)
  ```

+ 从另一个数组构建

  + 浅拷贝 具体请参考Object.assignI(target , source) 将array内存段赋予一个新的名字 两个变量操纵相同的内存

    ```js
    var array = [{name : 'a'},2,3,4,5,proc='a_proc'];
    var newArray = Object.assign(array , {}); //[1,2,3,4,5]
    array[2] = 'b'; 
    console.log(newArray);
    // [ { name: 'a' }, 2, 'b', 4, 5, 'a_proc' ]
    ```

  + 拷贝1 开辟新的内存 并原样拷贝原数组中的普通属性和引用属性

    ```js
    var array1 = [{name : 'a'},2,3,4,5,proc='a_proc'];
    var newArray1 = Array.from(array1); //[1,2,3,4,5]
    array1[2] = 'b';
    console.log(newArray1);
    // [ { name: 'a' }, 2, 3, 4, 5, 'a_proc' ]
    ```

    数组在存储引用属性时，仅仅存储他们在堆区中的引用 赋值前后的引用属性指向同一个堆区对象

    ```js
    var array2 = [{name : 'john'}];
    var newArray2 = Array.from(array2);
    console.log(newArray2[0].name); //john
    array2[0].name = "Sam";
    console.log(newArray2[0].name); //Sam 
    ```

    这样的过程同样发生在多维数组中

    ```js
    var array = [[1,2]]
    var newArray = Array.from(array);
    array[0][0] = 5;
    console.log(newArray); // [ [ 5, 2 ] ]
    ```

  + 如果需要深拷贝，则见mdn文档。[笔者认为这里js在这里设计非常不优雅或者说不合理]

+ 在拷贝中使用map函数

  ```js
  var array = [1,2,3,4,5]
  var doubledArray = Array.from(array, (value, index) => value+value);
  doubledArray; // [2,4,6,8,10];
  ```

+  以某个长度创建数组

  ```js
  function fillArray(length) {
      var obj = {length}; // 属性名简写
      return Array.from(obj, (val, index) => index);
  }
  console.log(fillArray(10));
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

  空洞在ForEach遍历不会被列出，因为ForEach会进行For...in检查

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
  const arr1 = [1 , 2 , false , 3 , 4];
  arr1['proc1'] = 'a_proc';
  for (let proc in arr1)
      console.log(arr1[proc]);
  // 1 2 a 3 4 a_proc
  ```

+ for of (ES6) 列出元素会含空洞

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

+ keys() 返回迭代器,包含所有可访问属性的索引，会为空洞返回索引 而Object.keys()不会

  + ```js
    var arr= [1,2,3];
    var keys= arr.keys(); // it returns an Array iterator 
      
    console.log(...keys) // ... 用于展开可迭代对象
    // 0 1 2
    ```

  + ```js
    var arr = [1,,3];
    Object.keys(arr); // [0,2]
    console.log(...arr.keys()) // 0,1,2
    
    // undefined is not a hole
    var arr = [1, undefined, 2]
    Object.keys(arr); // [0,1,2]
    console.log(...arr.keys()) // 0,1,2
    ```

+ values() 返回迭代器 包含所有可访问属性对应的值

  + ```js
    var array = ['🚒', '🚐', '🚚', '🚲'];
    var arrayIterator = array.values(); // Array iterator
    console.log(...arrayIterator) // 🚒,🚐,🚚,🚲
    // or we can iterate through iterator using for ... of
    for (let vehicle of arrayIterator) {
        console.log(vehicle);
    }
    output : 🚒,🚐,🚚,🚲
    ```


+ entries() 返回包含键值对的迭代器对象

  + ```js
    var array = ['a', 'b', 'c'];
    var iterator = array.entries();
    console.log(...iterator)
    // [0, "a"]  [1, "b"] [2, "c"]
    or we can use for..of
    for (let entry of iterator) {
      console.log(entry);
    }
    //  output
    [0, "a"]
    [1, "b"] 
    [2, "c"]
    or We can  use destructing
    for (const [index, element] of iterator )
      console.log(index, element);
    // output
    0 "a"
    1 "b"
    2 "c"
    ```







