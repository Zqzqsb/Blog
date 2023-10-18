# django的基本使用文档

## 应用的创建和启动
+ 建立新项目 
  
  python3 manage.py startapp app1

+ 启动顶级项目

  python3 manage.py runsever

+ 项目注册
  
  ![img_2.png](img_2.png)

+ 在顶级模块下建议对子模块的url映射

  ![img_3.png](img_3.png)

## 设计视图的对应URl
+ 视图
  + 添加在应用的views的中
  + 视图直接返回 HttpResonpse返回 或者 通过render渲染templates下面的http文件
  ![img.png](img.png)
  + 通过render渲染带占位符的html文件
  ![img_4.png](img_4.png)
  ![img_5.png](img_5.png)
+ url接口
  + 在应用目录下建立urls.py文件 该文件规定了url到视图的映射关系
  ![img_1.png](img_1.png)

## 数据库与数据模型
+ 链接mysql
  ![img_6.png](img_6.png)
+ 创建数据模型
  ![img_7.png](img_7.png)
+ 使用数据模型生成表结构
  + python3 manage.py makemigrations
  + python3 manage.py migrate
+ 修改表
  + 删除 可直接注释
  + 添加
    + default 字段
    + null 字段 blank 字段
  + 数据操作
  ![img_8.png](img_8.png)