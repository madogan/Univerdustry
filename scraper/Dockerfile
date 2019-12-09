FROM python:3.6-alpine3.7
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
COPY . /app
WORKDIR /app
RUN apk update
RUN apk add --update libxslt-dev libssl1.0
RUN apk add --update --virtual .build-deps g++ gcc musl-dev python3-dev libffi-dev libressl-dev
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
RUN python3 -m pip install -r requirements.txt
RUN apk --purge del .build-deps
EXPOSE 7000
CMD python3 ./run.py
