docker rm -f jenkins
docker run -itd --name=jenkins -p 8081:8080 -u=root -v /etc/localtime:/etc/localtime -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /home/jenkins:/var/jenkins_home jenkins:2.375.3
