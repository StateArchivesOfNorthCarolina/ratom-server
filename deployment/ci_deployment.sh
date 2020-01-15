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

if [ -z "$KUBE_AUTH_CREATE_CONFIG" ]; then
    echo "Using default kube config"
else
    echo "Using kube config from environment"
    [ -z "$KUBE_AUTH_SSL_CA_CERT_DATA" ] && echo "Missing KUBE_AUTH_SSL_CA_CERT_DATA var" && exit 1
    kubectl config set-cluster $KUBE_AUTH_CONTEXT-cluster --server=$KUBE_AUTH_HOST
    kubectl config set clusters.microk8s-cluster.certificate-authority-data $KUBE_AUTH_SSL_CA_CERT_DATA
    kubectl config set-context $KUBE_AUTH_CONTEXT --cluster=$KUBE_AUTH_CONTEXT-cluster --user=$KUBE_AUTH_USERNAME
    kubectl config set-credentials $KUBE_AUTH_USERNAME --username=$KUBE_AUTH_USERNAME --password=$KUBE_AUTH_PASSWORD
    kubectl config use-context $KUBE_AUTH_CONTEXT
fi

echo $VAULT_PASS > .vault_pass
ansible-galaxy install -r requirements.yaml
ansible-playbook deploy.yaml -l ratom-staging -e k8s_container_image_tag=$TAG
