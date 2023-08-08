FROM python:3.11
MAINTAINER Tester
WORKDIR /
COPY ./requirements.txt /
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && /bin/bash -c "pip install -r /requirements.txt -i https://mirrors.aliyun.com/pypi/simple/"


