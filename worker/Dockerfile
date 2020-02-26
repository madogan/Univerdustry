FROM python:3.6-alpine3.7
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apk update
RUN apk upgrade
RUN apk add --update make
RUN apk add postgresql-libs
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev
RUN apk add build-base alpine-sdk
RUN python3 -m pip install --upgrade pip setuptools
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN apk --purge del .build-deps
RUN apk add --no-cache tzdata
RUN echo $TZ > /etc/timezone
COPY . /application
WORKDIR /application
COPY worker /root/.pysnmp/mibs/ALLCONFIG-MIB.py
EXPOSE 5090
