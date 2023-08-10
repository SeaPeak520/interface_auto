#jenkins里要执行的命令

#删除容器，防止启动失败
docker rm -f auto_project
#启动容器并执行命令
-w 指定容器启动后的默认工作目录
#--volumes-from 指定共享容器 将jenkins工作空间的代码映射到python容器，会生成匿名容器卷，
# --rm 容器停止时，容器被自动删除，匿名卷也删除
#-w 指定容器启动后的默认工作目录
docker run -itd --name auto_project --rm -w=$WORKSPACE --volumes-from=jenkins -v /root/interface_auto:/auto --privileged=true python3.11:auto /bin/bash -c 'cd /auto;python main.py'
#查看用例执行情况
docker logs -f --tail=100 auto_project
#结束命令
exit 0