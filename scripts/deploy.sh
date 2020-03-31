#! /bin/bash

echo "Deploying..."

sed -i "s/<DB_USER>/${DB_USER}/g" ./manifests/database/config.yaml
sed -i "s/<DB_PASS>/${DB_PASS}/g" ./manifests/database/config.yaml
sed -i "s/<DB_NAME>/${DB_NAME}/g" ./manifests/database/config.yaml
sed -i "s/<NR_USER>/${NR_USER}/g" ./manifests/collector/config.yaml
sed -i "s/<NR_PASS>/${NR_PASS}/g" ./manifests/collector/config.yaml
sed -i "s/<DB_USER>/${DB_USER}/g" ./manifests/collector/config.yaml
sed -i "s/<DB_PASS>/${DB_PASS}/g" ./manifests/collector/config.yaml
sed -i "s/<DB_NAME>/${DB_NAME}/g" ./manifests/collector/config.yaml
sed -i "s/<DB_USER>/${DB_USER}/g" ./manifests/dash/config.yaml
sed -i "s/<DB_PASS>/${DB_PASS}/g" ./manifests/dash/config.yaml
sed -i "s/<DB_NAME>/${DB_NAME}/g" ./manifests/dash/config.yaml

kubectl apply -f manifests/database
kubectl apply -f manifests/collector
kubectl apply -f manifests/dash

sed -i "s/${DB_USER}/<DB_USER>/g" ./manifests/database/config.yaml
sed -i "s/${DB_PASS}/<DB_PASS>/g" ./manifests/database/config.yaml
sed -i "s/${DB_NAME}/<DB_NAME>/g" ./manifests/database/config.yaml
sed -i "s/${NR_USER}/<NR_USER>/g" ./manifests/collector/config.yaml
sed -i "s/${NR_PASS}/<NR_PASS>/g" ./manifests/collector/config.yaml
sed -i "s/${DB_USER}/<DB_USER>/g" ./manifests/collector/config.yaml
sed -i "s/${DB_PASS}/<DB_PASS>/g" ./manifests/collector/config.yaml
sed -i "s/${DB_NAME}/<DB_NAME>/g" ./manifests/collector/config.yaml
sed -i "s/${DB_USER}/<DB_USER>/g" ./manifests/dash/config.yaml
sed -i "s/${DB_PASS}/<DB_PASS>/g" ./manifests/dash/config.yaml
sed -i "s/${DB_NAME}/<DB_NAME>/g" ./manifests/dash/config.yaml

echo "DONE!"