#!/bin/bash
set -e
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "Pushing images to Docker Hub"
ansible-playbook -i deployment/inventory.yaml deployment/docker-hub.yaml -vv

# if ["$TRAVIS_BRANCH" == "staging"];
# then

    echo "Deploying to staging"

    cd ./deployment
    # K8S_AUTH_SSL_CA_CERT=./k8s-ca-cert

    if [ -z "$K8S_AUTH_CREATE_CONFIG" ]; then
        echo "Using default kube config"
    else
        echo "Using kube config from environment"
        [ -z "$K8S_AUTH_SSL_CA_CERT_DATA" ] && echo "Missing K8S_AUTH_SSL_CA_CERT_DATA var" && exit 1
        # echo $K8S_AUTH_SSL_CA_CERT_DATA | base64 --decode > $K8S_AUTH_SSL_CA_CERT
        kubectl config set-cluster $K8S_AUTH_CONTEXT-cluster --server=$K8S_AUTH_HOST #--certificate-authority=$K8S_AUTH_SSL_CA_CERT --embed-certs=true
        kubectl config set clusters.microk8s-cluster.certificate-authority-data $K8S_AUTH_SSL_CA_CERT_DATA
        kubectl config set-context $K8S_AUTH_CONTEXT --cluster=$K8S_AUTH_CONTEXT-cluster --user=$K8S_AUTH_USERNAME
        kubectl config set-credentials $K8S_AUTH_USERNAME --username=$K8S_AUTH_USERNAME --password=$K8S_AUTH_PASSWORD
        kubectl config use-context $K8S_AUTH_CONTEXT
    fi

    ansible-galaxy install -r requirements.yaml
    ansible-playbook deploy.yaml -l ratom-staging -vvvv

# fi
