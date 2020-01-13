#!/bin/bash
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "Pushing images to Docker Hub"
ansible-playbook deployment/docker-hub.yaml -vv

if ["$TRAVIS_BRANCH" == "staging"];
then
    echo "Deploying to staging"
fi