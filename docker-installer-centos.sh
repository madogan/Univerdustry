#!/bin/bash

# Install needed packages
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# Configure the docker-ce repo
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install docker-ce
sudo yum install docker-ce

# Add your user to the docker group with the following command
sudo usermod -aG docker $(whoami)

# Set Docker to start automatically at boot time
sudo systemctl enable docker.service

# start the Docker service
sudo systemctl start docker.service

# DOCKER-COMPOSE INSTALLATION

# Install Extra Packages for Enterprise Linux
sudo yum install epel-release

# Install python-pip
sudo yum install -y python-pip

# Install docker-compose
sudo pip install docker-compose

# Upgrade your Python packages on CentOS 7 to get docker-compose to run 
sudo yum upgrade python*
