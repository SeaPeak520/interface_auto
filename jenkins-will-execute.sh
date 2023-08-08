#jenkins里要执行的命令

#删除容器，防止启动失败
docker rm -f auto_project
#启动容器并执行命令
docker run -itd --name auto_project --rm -w=$WORKSPACE --volumes-from=jenkins -v /root/interface_auto:/auto --privileged=true python3.11:auto /bin/bash -c 'cd /auto;python main.py'
#睡眠，等待用例执行生成allure测试数据，防止下面生成报告时 空数据
sleep 10s
#结束命令
exit 0