FROM python:3.6-buster
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN echo $TZ > /etc/timezone
RUN apt-get update && apt-get upgrade -y && apt-get -y install gcc musl-dev libffi-dev
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY . /application
WORKDIR /application
EXPOSE 7000
