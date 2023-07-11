# docker使用

+ docker command --help
+ docker images
  + 显示所有本地镜像
+ docker search mysql --filter-stars=3000
  + 搜索
+ docker pull mysql
  + 下载镜像
+ docker rmi -f $(docker images -aq)
  + 删除全部镜像
+ docker run [optional] image
  + -name 容器名
  + -d 后台
  + -it 交互
  + -p 容器端口: 容器端口
  + -P 随机端口
+ docker ps(列出所运行的容器)
  + -a -1
+ exit / Ctrl + P + Q
+ docker rm -f $(docker ps -aq)
+ docker logs - tf --tail 10 (containerid)