---
title: Linux 命令-进程
createTime: 2024-4-25
author: ZQ
tags:
	- linux
description: linux进程相关。
permalink: /linux_process/
---
<br> linux进程相关。
<!-- more -->

## ps

- `a`：显示所有终端机下的进程，包括其他用户的进程。
- `u`：以用户为主的格式来显示进程状况。
- `x`：显示没有控制终端的进程。

##  free

该命令可以显示总的、已用的、可用的物理内存，以及交换空间的信息。

```shell
➜  ~ free -h
              total        used        free      shared  buff/cache   available
Mem:          1.9Gi       691Mi       436Mi        11Mi       785Mi       1.0Gi
Swap:            0           0           0
```

## top

该命令可以实时显示进程状态，类似于 Windows 的任务管理器。在 `top` 的界面中，可以看到内存的使用情况。

```shell
➜  ~ top
top - 16:58:01 up 26 days,  2:43,  1 user,  load average: 0.01, 0.01, 0.00
Tasks:  95 total,   1 running,  94 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.3 us,  0.2 sy,  0.0 ni, 99.5 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   1913.8 total,    436.0 free,    692.0 used,    785.8 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.   1032.7 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
  699 root      10 -10  141356  22920      0 S   1.0   1.2 212:57.52 AliYunDunMonito
  551 root      20   0  689564  14572   9552 S   0.3   0.7  31:55.13 aliyun-service
  611 root      20   0 2517508 266936   1292 S   0.3  13.6 208:06.56 nessusd
  626 root      20   0   42184    964      0 S   0.3   0.0  23:46.46 AliYunDunUpdate
  687 root      10 -10   88304   8836   6200 S   0.3   0.5 125:00.14 AliYunDun
15417 root      20   0  724344   5448      0 S   0.3   0.3   4:03.85 clash-linux-amd
    1 root      20   0  169528   5552   3140 S   0.0   0.3   0:29.79 systemd
    2 root      20   0       0      0      0 S   0.0   0.0   0:00.00 kthreadd
```

## vmstat

```shell
➜  ~ vmstat
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 446244  90108 714600    0    0   371    43    9    2  0  0 98  1  0
```

## 通过进程名 查看进程打开文件的句柄

```shell
systemctl show --property MainPID --value nessusd | xargs -I {} lsof -p {}
```

```shell
COMMAND   PID USER   FD   TYPE             DEVICE SIZE/OFF    NODE NAME
nessus-se 554 root  cwd    DIR              254,1     4096       2 /
nessus-se 554 root  rtd    DIR              254,1     4096       2 /
nessus-se 554 root  txt    REG              254,1    39456 1317347 /opt/nessus/sbin/nessus-service
nessus-se 554 root  mem    REG              254,1  1824496  787069 /usr/lib/x86_64-linux-gnu/libc-2.28.so
nessus-se 554 root  mem    REG              254,1   100712  786453 /usr/lib/x86_64-linux-gnu/libgcc_s.so.1
nessus-se 554 root  mem    REG              254,1  1579448  787072 /usr/lib/x86_64-linux-gnu/libm-2.28.so
nessus-se 554 root  mem    REG              254,1  1570256  789763 /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
nessus-se 554 root  mem    REG              254,1   146968  787087 /usr/lib/x86_64-linux-gnu/libpthread-2.28.so
nessus-se 554 root  mem    REG              254,1    14592  787071 /usr/lib/x86_64-linux-gnu/libdl-2.28.so
nessus-se 554 root  mem    REG              254,1    19048  786461 /usr/lib/x86_64-linux-gnu/libanl-2.28.so
nessus-se 554 root  mem    REG              254,1   165632  786455 /usr/lib/x86_64-linux-gnu/ld-2.28.so
nessus-se 554 root    0r   CHR                1,3      0t0      21 /dev/null
nessus-se 554 root    1u  unix 0x0000000053591e84      0t0   14700 type=STREAM
nessus-se 554 root    2u  unix 0x0000000053591e84      0t0   14700 type=STREAM
```
## 通过进程名 查看其网络连接状态

```shell
➜  ~ lsof -i -P -n | grep nessusd
nessusd     611     root   19u  IPv4 7391772      0t0  TCP *:8834 (LISTEN)
nessusd     611     root   20u  IPv6 7391773      0t0  TCP *:8834 (LISTEN)
```

## 查看本机进程和外部端口的数据包

```shell
tcpdump -i eth0 tcp port 8834 and host 222.70.235.176
```

```shell
17:24:08.675102 IP 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53238 > AliCloud-2C2G.8834: Flags [S], seq 484590853, win 65535, options [mss 1452,nop,wscale 6,nop,nop,TS val 3440648465 ecr 0,sackOK,eol], length 0
17:24:08.675160 IP AliCloud-2C2G.8834 > 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53238: Flags [S.], seq 724970684, ack 484590854, win 28960, options [mss 1460,sackOK,TS val 3618397675 ecr 3440648465,nop,wscale 7], length 0
17:24:08.675695 IP 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53239 > AliCloud-2C2G.8834: Flags [S], seq 287310922, win 65535, options [mss 1452,nop,wscale 6,nop,nop,TS val 4125725884 ecr 0,sackOK,eol], length 0
17:24:08.675705 IP AliCloud-2C2G.8834 > 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53239: Flags [S.], seq 1956095185, ack 287310923, win 28960, options [mss 1460,sackOK,TS val 3618397676 ecr 4125725884,nop,wscale 7], length 0
17:24:08.687070 IP 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53238 > AliCloud-2C2G.8834: Flags [.], ack 1, win 2070, options [nop,nop,TS val 3440648476 ecr 3618397675], length 0
17:24:08.687107 IP 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53238 > AliCloud-2C2G.8834: Flags [P.], seq 1:1766, ack 1, win 2070, options [nop,nop,TS val 3440648476 ecr 3618397675], length 1765
17:24:08.687120 IP AliCloud-2C2G.8834 > 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53238: Flags [.], ack 1766, win 254, options [nop,nop,TS val 3618397687 ecr 3440648476], length 0
17:24:08.687717 IP 176.235.70.222.broad.xw.sh.dynamic.163data.com.cn.53239 > AliCloud-2C2G.8834: Flags [.], ack 1, win 2070, options [nop,nop,TS val 4125725895 ecr 3618397676], length 0
```

## 找到某个服务的运行目录和所涉命令

```shell
➜  ~ systemctl list-units --type=service --state=running
```

```
UNIT                       LOAD   ACTIVE SUB     DESCRIPTION
aegis.service              loaded active running Aegis Service
aliyun.service             loaded active running Aliyun Assist
AssistDaemon.service       loaded active running AssistDaemon
chrony.service             loaded active running chrony, an NTP client/server
containerd.service         loaded active running containerd container runtime
cron.service               loaded active running Regular background program processing daemon
dbus.service               loaded active running D-Bus System Message Bus
docker.service             loaded active running Docker Application Container Engine
getty@tty1.service         loaded active running Getty on tty1
nessusd.service            loaded active running The Nessus Vulnerability Scanner
postgresql@11-main.service loaded active running PostgreSQL Cluster 11-main
rsyslog.service            loaded active running System Logging Service
serial-getty@ttyS0.service loaded active running Serial Getty on ttyS0
ssh.service                loaded active running OpenBSD Secure Shell server
systemd-journald.service   loaded active running Journal Service
systemd-logind.service     loaded active running Login Service
systemd-networkd.service   loaded active running Network Service
systemd-udevd.service      loaded active running udev Kernel Device Manager
user@0.service             loaded active running User Manager for UID 0
```

**CGroup**

Control Group是内核的一部分，用于限制，记录和隔离进程组使用的物理资源。

```shell
➜  ~ systemctl status nessusd
● nessusd.service - The Nessus Vulnerability Scanner
   Loaded: loaded (/lib/systemd/system/nessusd.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2024-03-30 14:14:37 CST; 3 weeks 5 days ago
 Main PID: 554 (nessus-service)
    Tasks: 16 (limit: 2261)
   Memory: 838.2M
   CGroup: /system.slice/nessusd.service
           ├─554 /opt/nessus/sbin/nessus-service -q
           └─611 nessusd -q

Mar 30 14:14:37 AliCloud-2C2G systemd[1]: Started The Nessus Vulnerability Scanner.
Mar 30 14:15:09 AliCloud-2C2G nessus-service[554]: Cached 286 plugin libs in 186msec
Mar 30 14:15:09 AliCloud-2C2G nessus-service[554]: Cached 286 plugin libs in 81msec
```

```
➜  ~ systemctl show --property MainPID nessusd.service --value

554
```

```shell
sudo ls -l /proc/554/cwd
```

```shell
➜  ~ sudo ls -l /proc/554/cwd
lrwxrwxrwx 1 root root 0 Apr 22 00:05 /proc/554/cwd -> /
```

## shell中一个线程读写文件 另一个线程可以删除这个文件吗

```shell
#!/bin/bash

# 创建一个名为testfile的文件
echo "Start" > testfile

# 启动一个子进程来循环写入文件
(
  while true; do
    echo "Writing to file..."
    echo "Data" >> testfile
    sleep 1
    #cat testfile
  done
) &

# 记住子进程的PID，以便稍后可以停止它
pid=$!

# 等待一会儿让写入进程有机会运行
sleep 5

# 删除文件
echo "Deleting file..."
rm testfile

echo "kill......"
sleep 2
# 停止写入进程
kill $pid


# 检查文件是否存在
if [[ -e testfile ]]; then
  echo "File exists"
else
  echo "File does not exist"
fi
```

>进程和线程都是操作系统进行资源分配和调度的基本单位，但是它们之间有一些关键的区别：

1. **独立性**：进程是系统资源分配的最小单位，线程是系统调度的最小单位。进程拥有独立的地址空间，每启动一个进程，系统就会为它分配独立的地址空间，建立数据表来维护代码段、堆栈段和数据段等信息。线程是进程的一部分，是比进程更小的能独立运行的基本单位，它复用父进程的地址空间，并共享其资源。
2. **开销**：由于进程具有独立的地址空间，因此进程之间的切换需要较大的开销。相比之下，线程可以看作轻量级的进程，同一进程内的线程切换开销小，因为它们可以共享相同的上下文。
3. **通信方式**：进程间通信（IPC）需要操作系统提供机制来进行，常见的进程间通信方式有管道、消息队列、信号量、共享内存等。而线程间可以直接通信，线程共享相同的地址空间，所以一个线程可以访问同一进程下的其他线程的数据，线程间通信更方便，开销更小。
4. **改变环境**：每个进程都有自己的独立环境，改变进程的执行环境（如改变工作目录、用户ID、打开文件等）不会影响其他进程。而线程共享进程的执行环境，一个线程改变了执行环境，其他线程也会受到影响。
5. **生命周期**：进程有自己的生命周期，从创建到终止。线程的生命周期则存在于进程的生命周期之内，线程的创建和终止都需要在其父进程的生命周期内完成。

综上，我们可以看出，子进程和线程既有相似之处，也有区别。它们都可以用于并发执行代码，但是由于它们的特性不同，所以在实际使用中，选择使用子进程还是线程，需要根据具体的需求和场景来决定。

>子进程和父进程是操作系统中进程间的一种重要关系。在多任务操作系统中，进程是资源分配和调度的基本单位。当一个进程创建了一个新的进程，创建的进程被称为子进程，而原进程被称为父进程。

 以下是父进程和子进程之间的一些关系：
1. **创建关系**：父进程是通过调用某种形式的创建进程的系统调用（例如 Unix 系统中的 `fork()` 函数）来创建子进程的。创建出来的子进程是父进程的副本，它继承了父进程的许多属性，如环境变量、打开的文件描述符等。
2. **资源共享**：子进程会继承父进程的环境设置和部分资源，但是子进程有自己的数据空间，子进程对数据的修改不会影响父进程。
3. **生命周期**：父进程和子进程的生命周期可以是独立的。父进程在创建子进程后可以继续执行其他任务，也可以等待子进程结束。同样，即使父进程结束，子进程也可以继续运行，这时的子进程通常被称为孤儿进程。
4. **进程间通信**：父进程和子进程可以通过各种进程间通信（IPC）机制进行通信，如管道、消息队列、共享内存等。
5. **进程ID**：每个进程都有一个唯一的进程ID。子进程有自己的新进程ID，同时还知道父进程的ID。父进程可以通过子进程的ID来控制或者接收子进程的状态信息。
父子进程机制是多任务系统实现并发处理的一种重要方式，通过进程的分裂，可以使得多个任务并行处理，提高系统的效率。 

```shell
Writing to file...
Writing to file...
Writing to file...
Writing to file...
Writing to file...
Deleting file...
File does not exist
[1]  + 25485 terminated  ( while true; do; echo "Writing to file..."; echo "Data" >> testfile; sleep 1)
```

## C++处理linux信号

在Linux中，有许多不同的信号可以发送给进程。以下是一些常见的信号：

1. `SIGINT`：当用户按下Ctrl+C时发送的中断信号。
2. `SIGQUIT`：当用户按下Ctrl+\时发送的退出信号。
3. `SIGTERM`：系统默认的终止信号，可以被进程捕获并决定如何处理。
4. `SIGKILL`：立即终止进程的信号，进程无法捕获或忽略此信号。
5. `SIGHUP`：通常用于指示控制终端已断开连接，但也常被用于其他目的，例如告诉守护进程重新读取其配置文件。
6. `SIGSEGV`：当进程执行了一个无效的内存引用时发送的信号，通常导致进程终止并转储核心。

```c++
#include <csignal>
#include <iostream>

void handle_sigint(int sig) {
    std::cout << "Caught signal " << sig << std::endl;
    // 在此处执行你希望在接收到SIGINT时执行的操作...
}

int main() {
    std::signal(SIGINT, handle_sigint);
    while (true) {
        // 你的程序主循环...
    }
    return 0;
}
```

在C++中，你可以使用`signal`函数来注册一个信号处理函数，这个函数将在接收到指定的信号时被调用。

在上面的例子中，我们定义了一个名为`handle_sigint`的函数，然后使用`std::signal(SIGINT, handle_sigint);`来注册它作为SIGINT信号的处理函数。这意味着，每当进程接收到SIGINT信号时，`handle_sigint`函数就会被调用。

请注意，不是所有的信号都可以被捕获。例如，SIGKILL和SIGSTOP信号不能被捕获，它们总是会立即终止进程或停止进程。


```shell
➜  General git:(master) ✗ ps -a | grep test                             
96928 ttys006    0:00.00 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox test
96146 ttys009    2:14.54 /Users/zq/WorkSpace/test
```

### 强制退出

```shell
➜  General git:(master) ✗ kill -SIGTERM 96146
```

```shell
➜  WorkSpace cd "/Users/zq/WorkSpace/" && g++ -std=c++17 test.cpp -o test && "/Users/zq/WorkSpace/"test
[1]    96146 terminated  "/Users/zq/WorkSpace/"test

```

### 退出信号

```shell
➜  General git:(master) ✗ kill -SIGINT 99123 
```

```shell
➜  WorkSpace cd "/Users/zq/WorkSpace/" && g++ -std=c++17 test.cpp -o test && "/Users/zq/WorkSpace/"test
Caught signal 2
```

程序继续运行。
## 通过端口号查看进程状态

```shell
➜  ~ lsof -i :8834
COMMAND PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
nessusd 611 root   19u  IPv4 7391772      0t0  TCP *:8834 (LISTEN)
nessusd 611 root   20u  IPv6 7391773      0t0  TCP *:8834 (LISTEN)
```

## 互斥和同步

互斥（Mutual Exclusion）和同步（Synchronization）是操作系统和并发编程中的重要概念。

1. **互斥**：互斥是一种机制，用于防止两个或多个进程（或线程）同时进入临界区域（即一次只能由一个进程访问的代码区域）并可能导致数据不一致的情况。这主要用于保护共享资源，如文件、内存或硬件设备，防止同时被多个进程修改。

2. **同步**：同步是一种机制，用于协调两个或多个进程（或线程）的执行顺序。这通常用于确保某些操作在其他操作之前或之后完成，或者用于等待某个条件成立（例如，等待另一个进程完成其工作）。

以下是Linux中实现互斥和同步的一些机制：

- **互斥锁（Mutex）**：互斥锁是一种最常用的互斥机制。一个进程在进入临界区之前需要获取互斥锁，如果锁已经被另一个进程持有，则该进程将阻塞（等待）。当持有锁的进程离开临界区时，它将释放锁，这样其他等待的进程就可以获取锁并进入临界区。

- **信号量（Semaphore）**：信号量可以被用来实现互斥和同步。一个信号量有一个与之关联的计数器，如果计数器大于0，那么获取信号量的进程可以继续执行；如果计数器等于0，那么获取信号量的进程将阻塞。信号量的计数器可以被任何持有该信号量的进程增加或减少。

- **条件变量（Condition Variable）**：条件变量常用于实现同步。一个进程可以等待一个条件变量，这将导致该进程阻塞，直到另一个进程触发该条件变量。这通常用于实现“等待某个条件成立”这样的同步。

- **管道（Pipe）和消息队列（Message Queue）**：管道和消息队列允许进程之间发送和接收数据，这也可以实现同步。例如，一个进程可以等待另一个进程通过管道发送的数据。

以上这些都是进程级别的互斥和同步机制。在线程级别，互斥和同步可以通过类似的机制实现，例如互斥锁、条件变量和barrier等。这些通常由线程库（如POSIX Threads或C++11中的std::thread）提供。

```c++
#include <stdio.h>
#include <pthread.h>

// 互斥锁和条件变量
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

// 产品数量
int products = 0;

// 生产者线程函数
void* producer(void* arg) {
    while (1) {
        pthread_mutex_lock(&mutex);

        products++;
        printf("Produced one product, total number of products: %d
", products);

        pthread_cond_signal(&cond);
        pthread_mutex_unlock(&mutex);
    }
}

// 消费者线程函数
void* consumer(void* arg) {
    while (1) {
        pthread_mutex_lock(&mutex);

        while (products == 0) {
            pthread_cond_wait(&cond, &mutex);
        }
        
        products--;
        printf("Consumed one product, total number of products: %d
", products);

        pthread_mutex_unlock(&mutex);
    }
}

int main() {
    pthread_t prod, cons;
    
    // 创建生产者和消费者线程
    pthread_create(&prod, NULL, producer, NULL);
    pthread_create(&cons, NULL, consumer, NULL);

    // 等待线程结束
    pthread_join(prod, NULL);
    pthread_join(cons, NULL);

    return 0;
}

```

在这个例子中，我们有一个生产者线程和一个消费者线程。生产者线程生产产品，消费者线程消费产品。

当生产者生产一个产品时，它会锁定互斥锁，增加产品数量，然后解锁互斥锁，并发送一个条件变量信号来唤醒可能正在等待产品的消费者线程。

消费者线程会尝试锁定互斥锁，然后检查产品数量。如果产品数量为0，它会等待条件变量。当生产者线程发送条件变量信号时，消费者线程会被唤醒，然后消费一个产品，解锁互斥锁。


## 优雅停止

优雅的停止机制通常意味着当你想要停止程序时，程序能够完成当前的工作，清理使用的资源，然后安全地退出，而不是立即停止并可能导致数据丢失或者资源泄漏。

一般通过 handle_signal() 处理SIGINT信号实现。
