FROM jenkins/jenkins:2.375.3-jdk11
MAINTAINER Tester
WORKDIR /
USER root
COPY ./env_path /
ADD ./allure-2.21.0.tgz /
ADD ./jdk-11.0.18_linux-x64_bin.tar.gz /
RUN ln -s /allure-2.21.0/bin/allure /usr/bin/allure && /bin/bash -c "ln -s /jdk-11.0.18/bin/java /usr/bin/java" && /bin/bash -c "cat /env_path >> /root/.bashrc" && /bin/bash -c "source /root/.bashrc"

