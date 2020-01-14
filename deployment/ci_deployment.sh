#!/bin/bash
set -e
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "Pushing images to Docker Hub"
ansible-playbook -i deployment/inventory.yaml deployment/docker-hub.yaml -vv

# if ["$TRAVIS_BRANCH" == "staging"];
# then

    echo "Deploying to staging"

    cd ./deployment
    # KUBE_AUTH_SSL_CA_CERT_DATA=./k8s-ca-cert

    if [ -z "$KUBE_AUTH_CREATE_CONFIG" ]; then
        echo "Using default kube config"
    else
        echo "Using kube config from environment"
        [ -z "$KUBE_AUTH_SSL_CA_CERT_DATA" ] && echo "Missing KUBE_AUTH_SSL_CA_CERT_DATA var" && exit 1
        # echo $KUBE_AUTH_SSL_CA_CERT_DATA | base64 --decode > $KUBE_AUTH_SSL_CA_CERT_DATA
        kubectl config set-cluster $KUBE_AUTH_CONTEXT-cluster --server=$KUBE_AUTH_HOST #--certificate-authority=$K8S_AUTH_SSL_CA_CERT --embed-certs=true
        kubectl config set clusters.microk8s-cluster.certificate-authority-data $KUBE_AUTH_SSL_CA_CERT_DATA
        kubectl config set-context $KUBE_AUTH_CONTEXT --cluster=$KUBE_AUTH_CONTEXT-cluster --user=$KUBE_AUTH_USERNAME
        kubectl config set-credentials $KUBE_AUTH_USERNAME --username=$KUBE_AUTH_USERNAME --password=$KUBE_AUTH_PASSWORD
        kubectl config use-context $KUBE_AUTH_CONTEXT
    fi

    kubectl config view
    kubectl cluster-info
    ansible-galaxy install -r requirements.yaml
    ansible-playbook deploy.yaml -l ratom-staging -vvvv

# fi
