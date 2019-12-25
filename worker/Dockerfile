FROM python:3.6-alpine3.7
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
COPY ../operator /app
WORKDIR /app
RUN apk update
RUN apk add postgresql-libs
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r requirements.txt
RUN apk --purge del .build-deps
