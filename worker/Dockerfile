FROM python:3.6-alpine3.7
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apk update
RUN apk upgrade
RUN apk add --update make
RUN apk add --virtual .build-deps jpeg-dev zlib-dev libjpeg  gcc musl-dev libffi-dev
RUN apk add build-base alpine-sdk
RUN python3 -m pip install --upgrade pip setuptools
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN apk --purge del .build-deps
RUN apk add --no-cache tzdata
RUN echo $TZ > /etc/timezone
COPY . /application
WORKDIR /application
EXPOSE 8000
