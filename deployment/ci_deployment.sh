#!/bin/bash
set -e

echo "Tagging images"
BRANCH_CLEAN=$(echo $TRAVIS_BRANCH | sed "s@/@-@")
TAG=${BRANCH_CLEAN}-${TRAVIS_COMMIT:0:7}
docker tag $DOCKERHUB_REPO $DOCKERHUB_REPO:$TAG
docker tag $DOCKERHUB_REPO $DOCKERHUB_REPO:latest

echo "Pushing images to Docker Hub"
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push $DOCKERHUB_REPO:$TAG
docker push $DOCKERHUB_REPO:latest

echo "Deploying to staging"
cd ./deployment

echo $VAULT_PASS > .vault_pass
ansible-galaxy install -r requirements.yaml
ansible-playbook deploy.yaml -l $DEPLOY_HOST -e k8s_container_image_tag=$TAG
