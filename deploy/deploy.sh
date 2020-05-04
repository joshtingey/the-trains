#! /bin/bash

ENV=$(read_var ENV .env)
if [ "$ENV" == "prod" ]; then

    # Setup the environment variables from the .env file if not already exported
    [[ -z "${CERT_EMAIL}" ]] && CERT_EMAIL=$(sed -n 's/CERT_EMAIL=//p' .env)
    [[ -z "${MONGO_INITDB_ROOT_USERNAME}" ]] && MONGO_INITDB_ROOT_USERNAME=$(sed -n 's/MONGO_INITDB_ROOT_USERNAME=//p' .env)
    [[ -z "${MONGO_INITDB_ROOT_PASSWORD}" ]] && MONGO_INITDB_ROOT_PASSWORD=$(sed -n 's/MONGO_INITDB_ROOT_PASSWORD=//p' .env)
    [[ -z "${DOMAIN}" ]] && DOMAIN=$(sed -n 's/DOMAIN=//p' .env)
    [[ -z "${K8S_SERVER}" ]] && K8S_SERVER=$(sed -n 's/K8S_SERVER=//p' .env)
    [[ -z "${K8S_CERTIFICATE}" ]] && K8S_CERTIFICATE=$(sed -n 's/K8S_CERTIFICATE=//p' .env)
    [[ -z "${K8S_TOKEN}" ]] && K8S_TOKEN=$(sed -n 's/K8S_TOKEN=//p' .env)

    # Setup the production cluster with kubectl
    kubectl config set-cluster production --server="${K8S_SERVER}"
    kubectl config set clusters.production.certificate-authority-data ${K8S_CERTIFICATE}
    kubectl config set-credentials production --token="${K8S_TOKEN}"
    kubectl config set-context production --cluster=production --user=production
    kubectl config use-context production

    # Insert environment variables into manifests
    sed -i "s/<CERT_EMAIL>/${CERT_EMAIL}/g" ./deploy/setup.yaml
    sed -i "s/<MONGO_INITDB_ROOT_USERNAME>/${MONGO_INITDB_ROOT_USERNAME}/g" ./deploy/mongo.yaml
    sed -i "s/<MONGO_INITDB_ROOT_PASSWORD>/${MONGO_INITDB_ROOT_PASSWORD}/g" ./deploy/mongo.yaml
    sed -i "s/<DOMAIN>/${DOMAIN}/g" ./deploy/thetrains.yaml

    # Deploy to the production cluster
    echo "Deploying to $DOMAIN($K8S_SERVER)"
    echo "With mongo $MONGO_INITDB_ROOT_USERNAME:$MONGO_INITDB_ROOT_PASSWORD"
    echo "And certificate email $CERT_EMAIL"
    #kubectl apply -f ./deploy/setup.yaml
    #kubectl apply -f ./deploy/mongo.yaml
    #kubectl apply -f ./deploy/collector.yaml
    #kubectl apply -f ./deploy/thetrains.yaml
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

