# Dockerfile - this is a comment. Delete me if you want.

# Base image is Ubuntu 16.04 LTS
FROM ubuntu:16.04

# Postgresql installation
# Add the PostgreSQL PGP key to verify their Debian packages.
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository. It contains the most recent stable release
#     of PostgreSQL, ``9.3``.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Get latest upgrades and install python3.6
RUN apt-get update
RUN apt-get install -y python-software-properties software-properties-common
# Postgresql pkgs and libpq-dev for netmiko -> psycopg2 dependency issue https://stackoverflow.com/questions/11618898/pg-config-executable-not-found
RUN apt-get install -y postgresql-9.3 postgresql-client-9.3 libpq-dev postgresql-contrib-9.3
RUN apt-get install -y netcat
# Install python3.6
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip curl vim nano
RUN python3.6 -m pip install pip --upgrade

RUN python3.6 -m pip install --upgrade pip
RUN python3.6 -m pip install --upgrade setuptools

COPY requirements.txt requirements.txt

# Install our dependencies
RUN python3.6 -m pip install -r requirements.txt

RUN apt-get update && apt-get -y install cron

# Copy our source code to workdir
COPY . /scraper
WORKDIR /scraper

# CHANGE the 8000 port according to gunicorn parameter in api/app.py
EXPOSE 5090

RUN apt-get update && apt-get -y install cron

# Copy hello-cron file to the cron.d directory
COPY scraper-cron /etc/cron.d/scraper-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/scraper-cron

# Apply cron job
RUN crontab /etc/cron.d/scraper-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
