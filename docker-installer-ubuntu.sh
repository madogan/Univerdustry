#!/bin/bash

# Update repositories
apt-get update

# Remove/uninstall old docker configuration
apt-get remove docker docker-engine docker.io

# Install docker
apt install docker.io

# Start docker service
systemctl start docker

# Enable docker service
systemctl enable docker

# Install docker version
curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Give exec perm to docker-compose binary
chmod +x /usr/local/bin/docker-compose
