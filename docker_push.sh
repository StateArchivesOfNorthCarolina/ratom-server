#!/bin/bash
echo "Pushing images to Docker Hub"
ansible-playbook deployment/docker-hub.yaml -vv