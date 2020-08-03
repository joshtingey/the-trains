#! /bin/bash

read_var() {
    VAR=$(grep "$1" "$2" | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo "${VAR[1]}"
}

ENV=$(read_var ENV .env)
if [ "$ENV" == "prod" ]; then
    # Insert environment variables into manifests
    sed -i "s/<CERT_EMAIL>/${CERT_EMAIL}/g" ./k8s/setup/certificates.yaml
    sed -i "s/<MONGO_INITDB_ROOT_USERNAME>/${MONGO_INITDB_ROOT_USERNAME}/g" ./k8s/setup/mongo.yaml
    sed -i "s/<MONGO_INITDB_ROOT_PASSWORD>/${MONGO_INITDB_ROOT_PASSWORD}/g" ./k8s/setup/mongo.yaml
    sed -i "s/<DOMAIN>/${DOMAIN}/g" ./k8s/setup/ingress.yaml

    # Deploy to the production cluster
    echo "Using $DOMAIN($K8S_SERVER)"
    echo "Setting up namespace..." && kubectl apply -f ./k8s/setup/namespace.yaml
    echo "Setting up MongoDB..." && kubectl apply -f ./k8s/setup/mongo.yaml
    echo "Setting up certificates..." && kubectl apply -f ./k8s/setup/certificates.yaml && sleep 60
    echo "Setting up service..." && kubectl apply -f ./k8s/setup/service.yaml
    echo "Setting up ingress..." && kubectl apply -f ./k8s/setup/ingress.yaml
    
    # Remove the environment variables from the manifests
    sed -i "s/${CERT_EMAIL}/<CERT_EMAIL>/g" ./k8s/setup/certificates.yaml
    sed -i "s/${MONGO_INITDB_ROOT_USERNAME}/<MONGO_INITDB_ROOT_USERNAME>/g" ./k8s/setup/mongo.yaml
    sed -i "s/${MONGO_INITDB_ROOT_PASSWORD}/<MONGO_INITDB_ROOT_PASSWORD>/g" ./k8s/setup/mongo.yaml
    sed -i "s/${DOMAIN}/<DOMAIN>/g" ./k8s/setup/ingress.yaml
else
    echo "ENV is not 'prod', will not continue!"
fi
