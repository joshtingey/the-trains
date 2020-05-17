#! /bin/bash

read_var() {
    VAR=$(grep $1 $2 | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo ${VAR[1]}
}

ENV=$(read_var ENV .env)
if [ "$ENV" == "prod" ]; then

    # Insert environment variables into manifests
    sed -i "s/<CERT_EMAIL>/${CERT_EMAIL}/g" ./deploy/setup.yaml
    sed -i "s/<MONGO_INITDB_ROOT_USERNAME>/${MONGO_INITDB_ROOT_USERNAME}/g" ./deploy/mongo.yaml
    sed -i "s/<MONGO_INITDB_ROOT_PASSWORD>/${MONGO_INITDB_ROOT_PASSWORD}/g" ./deploy/mongo.yaml
    sed -i "s/<DOMAIN>/${DOMAIN}/g" ./deploy/thetrains.yaml

    # Deploy to the production cluster
    echo "Deploying to $DOMAIN($K8S_SERVER)"
    echo "Apply setup.yaml" && kubectl apply -f ./deploy/setup.yaml && sleep 5
    echo "Apply mongo.yaml" && kubectl apply -f ./deploy/mongo.yaml && sleep 5
    echo "Apply collector.yaml" && kubectl apply -f ./deploy/collector.yaml && sleep 5
    echo "Apply thetrains.yaml" && kubectl apply -f ./deploy/thetrains.yaml && sleep 5
    #kubectl rollout restart deployment thetrains -n thetrains

    # Remove the environment variables from the manifests
    sed -i "s/${CERT_EMAIL}/<CERT_EMAIL>/g" ./deploy/setup.yaml
    sed -i "s/${MONGO_INITDB_ROOT_USERNAME}/<MONGO_INITDB_ROOT_USERNAME>/g" ./deploy/mongo.yaml
    sed -i "s/${MONGO_INITDB_ROOT_PASSWORD}/<MONGO_INITDB_ROOT_PASSWORD>/g" ./deploy/mongo.yaml
    sed -i "s/${DOMAIN}/<DOMAIN>/g" ./deploy/thetrains.yaml
    echo "DONE!"

else
    echo "ENV is not 'prod', will not continue!"
fi

