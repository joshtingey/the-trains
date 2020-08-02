#! /bin/bash

C_BLUE=`tput setaf 4`
C_RESET=`tput sgr0`

CURRENTDIR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

if [ -d ".venv/" ]
then
    echo "${C_BLUE}INFO:${C_RESET}    Activating python environment"
    source .venv/bin/activate
else
    echo "${C_BLUE}INFO:${C_RESET}    Creating python environment"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r ./app/requirements.txt -r ./app/common/requirements.txt -r ./app/thetrains/requirements.txt -r ./app/collector/requirements.txt
fi

echo "${C_BLUE}INFO:${C_RESET}    Exporting environment variables"
[[ -z "${CERT_EMAIL}" ]] && export CERT_EMAIL=$(sed -n 's/CERT_EMAIL=//p' .env)
[[ -z "${MONGO_INITDB_ROOT_USERNAME}" ]] && export MONGO_INITDB_ROOT_USERNAME=$(sed -n 's/MONGO_INITDB_ROOT_USERNAME=//p' .env)
[[ -z "${MONGO_INITDB_ROOT_PASSWORD}" ]] && export MONGO_INITDB_ROOT_PASSWORD=$(sed -n 's/MONGO_INITDB_ROOT_PASSWORD=//p' .env)
[[ -z "${DOMAIN}" ]] && export DOMAIN=$(sed -n 's/DOMAIN=//p' .env)
[[ -z "${K8S_SERVER}" ]] && export K8S_SERVER=$(sed -n 's/K8S_SERVER=//p' .env)
[[ -z "${K8S_CERTIFICATE}" ]] && export K8S_CERTIFICATE=$(sed -n 's/K8S_CERTIFICATE=//p' .env)
[[ -z "${K8S_TOKEN}" ]] && export K8S_TOKEN=$(sed -n 's/K8S_TOKEN=//p' .env)

STATUS=$(kubectl config get-clusters)
STATUS=${STATUS//$'\n'/}
if [ "$STATUS" == "NAMEmicrok8s-cluster" ]
then
    echo "${C_BLUE}INFO:${C_RESET}    Deployment cluster already setup"
else
    echo "${C_BLUE}INFO:${C_RESET}    Setting up k8s deployment cluster"
    kubectl config set-cluster microk8s-cluster --server="${K8S_SERVER}"
    kubectl config set clusters.microk8s-cluster.certificate-authority-data ${K8S_CERTIFICATE}
    kubectl config set-credentials admin --token="${K8S_TOKEN}"
    kubectl config set-context microk8s --cluster=microk8s-cluster --user=admin
    kubectl config use-context microk8s
fi

export PYTHONPATH=$PYTHONPATH:$(pwd)/app
echo "${C_BLUE}INFO:${C_RESET}    Setup complete"
cd $CURRENTDIR

