---
title: Linux FIFO 的 O_NOBLOCK 模式
createTime: 2025-2-22
author: ZQ
tags:
  - linux
permalink: /Linux/ipc/fifo/noblock/
---

 本文讨论unix中的系统调用`open()`与其阻塞模式，具体为`O_NOBLOCK` 标记的添加与否对于读FIFO命名管道造成的影响。

<!-- more -->

## 1.unix 中的`open()`.

`open()`定义在头文件`<fcntl.h>`中。

`open()`的函数原型: `int open(const char *path , int aflag  , ... /* mode_t mode* */);`

亦或是:`int openat(int fd, const char *path , int aflag , ... /* mode_t mode* */);`

若成功，返回文件描述符`fd` , 若失败，返回`-1`。

最后一个写作 `...`的参数表明余下的参数的类型和数量可变，它们在创建新文件时发挥作用，也不是本次讨论的重点。

显然， `cosnt char* path`是 要开文件的名字（通常是绝对路径）。而`aflag`参数则有以下常量通过或运算`|`组成。

- `O_RDONlY`    只读打开

- `O_WRONlY`    只写打开

- `O_RDWR`        读写打开

- `O_EXEC`        只执行打开

- `O_SEARCH`    只搜索（对于目录有此选项）

  在以上五个常量中必须指定且只能指定一个，而以下常量为可选的。

  

  +  `O_APPEND`      	每次写入追加到文件末尾。
  +  `O_CLOEXEC `        把FD_CLOEXEC设定为文件描述符。
  +  `O_CREATE`          若文件不存在则创建， 需要指定文件权限位 ， 即mode_t 参数。
  +  `O_DIRECTORY `    若path指向的不为目录，则出错。
  +  `O_EXCL `              若同时指定O_CREATE且文件不存在，则出错。可以将测试文件存在和创建文件封装为原子操作。
  +  `O_NOCTTY`          若path引用的是终端设备，则不将该设备分配作为该进程的控制终端。
+  `O_NONBLOCK`      若path引用的是一个FIFO，一个块特殊文件或者字符特殊文件，则此选项将本次文件的打开操作和后续的IO操作设置为非阻塞模式。
  +  `O_SYNC `              每次操作需要等待物理IO完成，包括更新文件属性而需要的物理IO。
+  `O_TURNC`            若文件存且为只写或读写打开，那么将其长度截断为零。
  +  `O_DSYNC`            每次写入需要等待物理IO完成，但是如果不影响读取，则不需要更新文件属性。
  +  `O_FSYNC`            使每一个 以文件描述符为参数的进行的read操作等待，直到所有对文件同一部分的挂起写操作都完成。    



## 2.FIFO的阻塞打开

FIFO是unix 中的命名管道，是unix系统中的IPC技术之一，用于支持进程间通信。FIFO的本质是文件。

创建FIFIO ： `mkfifo(const char* path , mode_t mode);`  \ `mkfifo(int fd , char* path , mode_t mode);` 

该函数原型定义在`<sys/stat.h>` 中。 若成功将返回`0` , 失败将返回`-1`。

如果path是绝对路径，则fd参数被忽略。若fd为相对路径，且fd是一个打开目录的有效文件描述符，那么最终路径名和目录有关。

环境： macos 11.2.3

头文件： 

```c
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/stat.h>
#define PIPE1 "/tmp/pipe1"
```

例子1 ， 阻塞打开FIFO：

```c
int main()
{
    //创建管道
    mkfifo(PIPE1 , 0777);
    //打开管道
    int fp1 = open(PIPE1 , O_WRONLY);
    printf("%d\n" , fp1);
}
```

运行程序，发现阻塞在`int fp1 = open(PIPE1 , O_WRONLY);`。

关于FIFO没有指定`O_NONBLOCK`标志的定义是这样的：**只读open要阻塞到某个进程为写而打开这个FIFO，同样只写open要阻塞到阻塞某个进程为度而打开它。**

在命令行中在目录/tmp/下查看FIFO是否被创建。

```shell
➜  /tmp ls -l  | grep pipe1 
prwxr-xr-x  1 zq    wheel    0 Apr 23 09:34 pipe1
```

可以看到pipe1 文件确实存在。 尝试使用cat来读取文件的内容。

```shell
➜  /tmp cat pipe1 
➜  /tmp 
```

可以看到cat 没有阻塞但是没有返回内容。 于此同时，main()函数不再阻塞，结束了运行。

```shell
3
Program ended with exit code: 0
```

**`3`是输出的文件描述符fp1 ,为什么是3？因为0，1，2 已经被标准输入，标准输出，和标准错误占用。它们伴随着程序的运行处于常开状态。cat没有输出内容也十分容易理解，因为main()程序中没有指定写入任何内容。同时印证了open之后的读操作是不会因为open没有指定`O_NONBLOCK`而随之阻塞。**

再次调用cat

```shell
➜  /tmp cat pipe1  

```

cat会立刻阻塞。

修改main()函数,并运行。

```c
int main()
{
    mkfifo(PIPE1 , 0777);                       /*创建管道*/
    int fp1 = open(PIPE1 , O_WRONLY);           /*以只读方式打开管道*/
    char buf[] = {'a' , 'b' , 'c'};             /*定义要发送的数据*/
    write(fp1 , buf , 3);                       /*写入数据*/
    close(fp1);                                 /*非必须，随之进程结束，打开的资源会被自动关闭*/
}
```

程序运行的同时，cat结束阻塞并输出写入的数据。

```shell
➜  /tmp cat pipe1  
abc                                                                                      
➜  /tmp
```

使用分别的个进程也可进行相同的验证，但是使用cat直接读取管道文件更加方便直观。



## 3.非阻塞标记`O_NONBLOCK`

### 只写非阻塞open()

观察程序

```c
int main()
{
    mkfifo(PIPE1 , 0777);
    int fp;
    char buf[] = {'a' , 'b' , 'c'};
    fp = open(PIPE1 , O_WRONLY | O_NONBLOCK);
    printf("file_descriptor: %d , errono: %d \n" , fp , errno);
    write(fp , buf , 3);
}
```

该程序试图向管道中写入数据，在不进行其他任何操作的情况下，管道没有任何读者。**在上文中，没有指定`O_NONBLOCK`的情况下，open操作将阻塞，直到有进程因为读取而打开这个管道。**而这里，open不会阻塞，但是在没有任何读者的情况下，open操作也不会成功。因为语句`printf("file_descriptor: %d , errono: %d \n" , fp , errno);`程序将有以下输出。

```shell
file_descriptor: -1 , errono: 6 
Program ended with exit code: 0
```

open返回-1，代表是打开操作失败，那么`write(fp , buf , 3);`, 就更不可能成功了。errno 是标准错误代码，可以在unix编程者手册中查到该错误代码的描述。

```shell
➜  /tmp man -a errno  
```

```shell
     6 ENXIO No such device or address.  Input or output on a special file
             referred to a device that did not exist, or made a request beyond
             the limits of the device.  This error may also occur when, for exam-
             ple, a tape drive is not online or no disk pack is loaded on a
             drive.
```

**那么以上可以得出，在没有读者的情况下，非阻塞写操作不能成功。**

**当然，如果有读者在阻塞等待，那么非阻塞写将成功，读者也能成功读到数据，可以先使用cat读取文件再启动写入程序来验证这一点。**



###  只读非阻塞open()

观察程序

```c
int main()
{
    mkfifo(PIPE1 , 0777);
    int fp;
    char buf[3];
    fp = open(PIPE1 , O_RDONLY | O_NONBLOCK);
    long nread = read(fp , buf , 3);
    printf("file_descriptor: %d , nread: %ld , errono: %d \n" , fp , nread ,  errno);
}
```

该程序试图以只读并且非阻塞方式打开一个空文件，那么在没有程序写入的情况下，显然它将什么也读不到。但是与非阻塞不同的是，open此时不是失败的，它成功的返回了描述，而read也显示读到文件末尾而非失败。

```shell
file_descriptor: 3 , nread: 0 , errono: 17 
Program ended with exit code: 0
```

而此时的errno: 17

```shell
     17 EEXIST File exists.  An existing file was mentioned in an inappropriate
             context, for instance, as the new link name in a link function.
```

事实上它不是open()或是read()设置的。可以在open和read之前将它输出来验证这一点。



## 4. 读写时序和数据存留

在上文的所有操作中，都是使用程序和cat命令来验证。但是，当打开和读写不再是原子操作时，(这里的原子操作， 并非绝对意义上的原子操作，而是打开和读写操作之间没有间隔，看上去就像同时发生的一样。)数据就会在在管道中存留。首先看一个例子。

```c
int main()
{
    mkfifo(PIPE1 , 0777);
    int fp;
    char buf[] = {'a' , 'b' , 'c'};
    pid_t pid = fork();
    if(pid == 0)
    {
        char buf1[3];
        fp = open(PIPE1 , O_RDONLY | O_NONBLOCK);
        int asleep = sleep(5);
        while(asleep > 0) asleep = sleep(asleep);
        /*打开文件后等待五秒,再尝试读取管道中的数据*/
        long nread = read(fp , buf1 , 3);
        printf("child process : file_descriptor: %d , nread: %ld \n" , fp , nread , errno);
        printf("child process : %s\n" , buf1);
        exit(1);
    }
    int asleep = sleep(2);/*在等待两秒后(等待子程序以只读方式打开管道),主程序立刻向管道非阻塞写入*/
    while(asleep > 0) asleep = sleep(asleep);
    fp = open(PIPE1 , O_WRONLY | O_NONBLOCK);
    long nwrite = write(fp , buf , 3);
    printf("main process : file_descriptor: %d , nwrite: %ld \n" , fp , nwrite);
  	printf("main process : wait for child process...\n");
    wait(NULL);/* 等待子程序结束*/
}
```

这段程序展示了两个进程在不同时刻写入和读取数据。这里因为在主程序语句`fp = open(PIPE1 , O_WRONLY | O_NONBLOCK);`发生之前，子程序就已经`fp = open(PIPE1 , O_RDONLY | O_NONBLOCK);`打开文件，所以主程序的打开操作能够成功。接着主程序向管道写入数据，子程序在等待一段时间后读取数据。

程序运行结果。

```shell
main process : file_descriptor: 3 , nwrite: 3 
main process : wait for child process...
child process : file_descriptor: 3 , nread: 3 
child process : abc
Program ended with exit code: 0
```

**可以看到这里的读取和写入都成功了，而且可以判断，在读写之间的这段时间里， 数据存在与管道中。**



## 5.抢占读取

在上一节的例子中，已经产生了数据会存留于管道之中的猜想。如何验证这一想法呢，很简单，只需要将上文中的子程序的等待时间设置的长些(如10s)， 在主程序等待子程序返回的时间内，使用别的程序（如cat）读取管道中的数据即可。

运行程序，主程序首先进入等待

```shell
main process : file_descriptor: 3 , nwrite: 3 
main process : wait for child process...
```

接着用cat读出管道中的数据

```shell
➜  /tmp cat pipe1  
abc
```

在主程序没有结束之前，cat也会随之阻塞。而这时的子程序则会什么都读不到

```shell
main process : file_descriptor: 3 , nwrite: 3 
main process : wait for child process...
child process : file_descriptor: 3 , nread: -1 
child process : 
Program ended with exit code: 0
```

**数据不会永久的存留于管道之中，当程序关闭，程序打开的文件描述符将被系统释放，管道中未被读取的数据也将被清空。（在既没有读者也没有写者的情况下）可以看到，命名管道用于ipc 通信时， 和操作系统中的经典问题——读着写者问题有相似也有不同之处。**