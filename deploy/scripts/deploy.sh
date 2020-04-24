#! /bin/bash

echo "Deploying..."

sed -i "s/<MONGO_INITDB_ROOT_USERNAME>/${MONGO_INITDB_ROOT_USERNAME}/g" ./manifests/mongo/config.yaml
sed -i "s/<MONGO_INITDB_ROOT_PASSWORD>/${MONGO_INITDB_ROOT_PASSWORD}/g" ./manifests/mongo/config.yaml

kubectl apply -f manifests/mongo
kubectl rollout restart deployment collector -n thetrains
kubectl rollout restart deployment thetrains -n thetrains

sed -i "s/${MONGO_INITDB_ROOT_USERNAME}/<MONGO_INITDB_ROOT_USERNAME>/g" ./manifests/mongo/config.yaml
sed -i "s/${MONGO_INITDB_ROOT_PASSWORD}/<MONGO_INITDB_ROOT_PASSWORD>/g" ./manifests/mongo/config.yaml

echo "DONE!"