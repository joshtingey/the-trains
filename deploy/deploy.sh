#! /bin/bash

read_var() {
    VAR=$(grep $1 $2 | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo ${VAR[1]}
}

ENV=$(read_var ENV .env)
if [ "$ENV" == "prod" ]; then
    echo "Deploying..."
    CERT_EMAIL=$(read_var CERT_EMAIL .env)
    MONGO_INITDB_ROOT_USERNAME=$(read_var MONGO_INITDB_ROOT_USERNAME .env)
    MONGO_INITDB_ROOT_PASSWORD=$(read_var MONGO_INITDB_ROOT_PASSWORD .env)
    DOMAIN=$(read_var DOMAIN .env)

    echo "Using CERT_EMAIL: $CERT_EMAIL"
    echo "Using MONGO_INITDB_ROOT_USERNAME: $MONGO_INITDB_ROOT_USERNAME"
    echo "Using MONGO_INITDB_ROOT_PASSWORD: $MONGO_INITDB_ROOT_PASSWORD"
    echo "Using DOMAIN: $DOMAIN"

    sed -i "s/<CERT_EMAIL>/${CERT_EMAIL}/g" ./deploy/setup.yaml
    sed -i "s/<MONGO_INITDB_ROOT_USERNAME>/${MONGO_INITDB_ROOT_USERNAME}/g" ./deploy/mongo.yaml
    sed -i "s/<MONGO_INITDB_ROOT_PASSWORD>/${MONGO_INITDB_ROOT_PASSWORD}/g" ./deploy/mongo.yaml
    sed -i "s/<DOMAIN>/${DOMAIN}/g" ./deploy/thetrains.yaml

    kubectl apply -f ./deploy/setup.yaml
    kubectl apply -f ./deploy/mongo.yaml
    kubectl apply -f ./deploy/collector.yaml
    kubectl apply -f ./deploy/thetrains.yaml
    #kubectl rollout restart deployment thetrains -n thetrains

    sed -i "s/${CERT_EMAIL}/<CERT_EMAIL>/g" ./deploy/setup.yaml
    sed -i "s/${MONGO_INITDB_ROOT_USERNAME}/<MONGO_INITDB_ROOT_USERNAME>/g" ./deploy/mongo.yaml
    sed -i "s/${MONGO_INITDB_ROOT_PASSWORD}/<MONGO_INITDB_ROOT_PASSWORD>/g" ./deploy/mongo.yaml
    sed -i "s/${DOMAIN}/<DOMAIN>/g" ./deploy/thetrains.yaml
    echo "DONE!"
else
    echo "ENV is not 'prod', will not continue!"
fi

