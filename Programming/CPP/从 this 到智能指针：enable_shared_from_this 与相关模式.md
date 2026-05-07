---
title: 从 this 到智能指针：enable_shared_from_this 与相关模式
createTime: 2026-05-03
author: ZQ
tags:
  - C++
  - Smart Pointer
  - CRTP
  - Boost
permalink: /programming/cpp/smart-ptr-from-this/
---

> 在成员函数里只有裸指针 `this`，却需要把当前对象交给异步回调、信号槽或另一个 `shared_ptr` 接口时，直接 `std::shared_ptr<T>(this)` 会制造**二次所有权**或**未定义行为**。标准库与 Boost 提供了一组「从自身取智能指针」的辅助基类。本文对比它们的用途、获取方式与选型，并说明它们与 **CRTP（Curiously Recurring Template Pattern）** 的关系。

<!-- more -->

---

## 1. 问题从哪来

`std::shared_ptr` 通过**控制块**统一管理引用计数与删除器。同一个对象只能对应**一个**这样的所有权链条；若在已有 `shared_ptr` 管理对象的前提下，再写：

```cpp
std::shared_ptr<Foo> p(this);  // 危险：与外部 shared_ptr 不共享控制块
```

会得到两个互不知情的 `shared_ptr`，析构时可能**二次 delete**，属于未定义行为。

正确做法是：**复用已有控制块**，再增加一次强引用。标准库把「当前对象已被某个 `shared_ptr` 管理」这一事实记在控制块里，并让你通过基类接口取出**同一块**上的新 `shared_ptr` 或 `weak_ptr`。这就是 `enable_shared_from_this` / `enable_weak_from_this` 要解决的问题。

---

## 2. 为什么说「核心思想是 CRTP」

这些辅助类都不是「写死的单一基类」，而是**模板基类，模板参数就是派生类自己**：

```cpp
class Widget : public std::enable_shared_from_this<Widget> {
  // ...
};
```

基类 `enable_shared_from_this<Widget>` 在实现里会把 `this` **安全地转换**为 `Widget*`，并与控制块协作生成 `shared_ptr<Widget>`。派生类名字出现在自己的基类模板实参里，这就是典型的 **CRTP**：用编译期已知的派生类型，在基类里提供与「具体子类型」绑定的行为，同时避免虚函数或运行时类型信息的额外成本（标准是否用虚表是实现细节，对使用者而言主要是**类型安全地回到派生类**）。

`std::enable_weak_from_this<T>` 同理，模板参数 `T` 也是 CRTP 式的「自己继承自己特化的基类」。

Boost 的侵入式引用计数基类（如 `intrusive_ref_counter` 一类）同样常见 **`Derived : public intrusive_ref_counter<Derived, ...>`** 的写法：计数与控制逻辑在基类里用 `Derived` 做完整类型优化，属于同一类设计思路。

---

## 3. 对比一览

| 类 / 模式 | 用途 | 获取方式 | C++ / 库版本 |
| --------- | ---- | -------- | ------------ |
| `enable_shared_from_this` | 获取与当前对象同一控制块的 `shared_ptr` | `shared_from_this()` | C++11 |
| `enable_weak_from_this` | 获取与当前对象同一控制块的 `weak_ptr` | `weak_from_this()` | C++17 |
| `intrusive_ref_counter`（Boost） | 侵入式引用计数，配合 `intrusive_ptr` | 常见惯用法为 `intrusive_ptr_from_this()`（或等价封装 / 从 `this` 构造 `intrusive_ptr`） | Boost |

说明：标准库前两者的命名空间为 `std::`。Boost 侵入式侧若使用第三方或项目封装，函数名可能与官方示例略有出入，语义上都是「在已建立侵入式所有权的前提下，从 `this` 再取一份一致的智能指针」。

---

## 4. `enable_shared_from_this`：默认首选

**适用**：绝大多数「对象生命周期已由 `shared_ptr` 接管」，且成员函数或回调里需要再交出一份**强引用**的场景（例如把 `shared_ptr` 捕获进 lambda、注册到需要 `shared_ptr` 的 API）。

**要点**：

- 只有在**至少已有一个** `shared_ptr` 拥有当前对象时，调用 `shared_from_this()` 才有定义；若在构造函数里、或尚未用 `shared_ptr` 接管的栈对象上调用，会抛 `std::bad_weak_ptr`（或等价未定义/实现定义行为，以标准为准）。
- 常见写法是：`std::make_shared<Derived>(...)` 或 `std::shared_ptr<Derived>(new Derived(...))` 作为**唯一**入口创建对象，之后内部再用 `shared_from_this()`。

**心智模型**：「我是在**同一条**所有权链上再 clone 一个 `shared_ptr`」，而不是新建一条链。

---

## 5. `enable_weak_from_this`：需要「旁观」时用

**适用**：

- 只希望观测对象是否仍存活、或临时 `lock()` 升级，而**不想**因为本次调用就强行延长对象生命（例如缓存、循环结构中的一环、调试探针）。
- 与 `shared_from_this` 一样依赖「已被 `shared_ptr` 管理」的前提；若尚未被管理，`weak_from_this()` 返回**空的** `weak_ptr`（与 `shared_from_this()` 抛异常的行为不同，这是 C++17 起弱引用接口的常见设计）。

**与循环引用**：`shared_ptr` 互相指向会形成环，导致计数永不为零。用 `weak_ptr` 断开其中一边，是经典解法之一；`weak_from_this()` 让你在不先升级成 `shared_ptr` 的前提下拿到 `weak_ptr`，便于在 API 上表达「弱持有」。

---

## 6. 侵入式引用计数：性能与约束的另一极

**思路**：引用计数存储在对象内部（或通过基类嵌入的钩子），`intrusive_ptr` 增减的是这份计数，往往**省掉单独的控制块分配**，缓存局部性更好，适合高性能或嵌入式风格代码。

**代价**：

- 侵入式：类型设计必须与计数策略绑定，文档与约束更多。
- 与 `std::shared_ptr` 互操作时通常需要明确边界（一般不混用两套所有权 unless 有清晰桥接）。

当你看到「性能敏感」「大量小对象」「希望减少堆分配」等关键词时，再评估 Boost（或自研）侵入式方案；否则维护成本更低的 `std::shared_ptr` + `enable_shared_from_this` 通常更划算。

---

## 7. 使用建议（小结）

1. **默认**：`std::enable_shared_from_this` + `shared_from_this()`，满足大部分从 `this` 安全升成 `shared_ptr` 的需求。
2. **避免循环引用或刻意弱化生命周期**：在需要 `weak_ptr` 语义处，用 `std::enable_weak_from_this` 与 `weak_from_this()`。
3. **极致性能或已有侵入式基础设施**：再考虑 Boost `intrusive_ref_counter` 一类方案，并统一团队的「从 this 构造 `intrusive_ptr`」规范。

---

## 8. 结语

`enable_shared_from_this` 与 `enable_weak_from_this` 解决的是**同一块控制块上的别名问题**；侵入式方案解决的是**另一套所有权表示下的性能与布局**。它们表面上 API 不同，底层却共享同一种工程化技巧：**用 CRTP 把「派生类自己」绑进基类模板**，从而在基类实现里安全地操作「当前对象的智能指针形态」。理解这一点后，读标准库头文件或 Boost 文档时，模板参数里那个「重复的派生类名」就不再神秘了。
