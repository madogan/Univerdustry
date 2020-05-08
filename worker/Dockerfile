FROM python:3.6-buster
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN echo $TZ > /etc/timezone
RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install gcc musl-dev libffi-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg topal libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade nltk
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader wordnet
RUN python3 -m nltk.downloader stopwords
RUN python3 -m pip install -r requirements.txt
COPY . /application
WORKDIR /application
