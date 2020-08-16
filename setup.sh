#! /bin/bash

C_BLUE=$(tput setaf 4)
C_RESET=$(tput sgr0)

CURRENTDIR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -d ".venv/" ]
then
    echo "${C_BLUE}INFO:${C_RESET}    Activating python environment"
    source .venv/bin/activate
else
    echo "${C_BLUE}INFO:${C_RESET}    Creating python environment"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r ./app/requirements.txt -r ./app/common/requirements.txt -r ./app/thetrains_app/requirements.txt -r ./app/data_collector/requirements.txt -r ./app/graph_generator/requirements.txt
fi

echo "${C_BLUE}INFO:${C_RESET}    Exporting environment variables"
[[ -z "${CERT_EMAIL}" ]] && export CERT_EMAIL=$(sed -n 's/CERT_EMAIL=//p' .env)
[[ -z "${MONGO_INITDB_ROOT_USERNAME}" ]] && export MONGO_INITDB_ROOT_USERNAME=$(sed -n 's/MONGO_INITDB_ROOT_USERNAME=//p' .env)
[[ -z "${MONGO_INITDB_ROOT_PASSWORD}" ]] && export MONGO_INITDB_ROOT_PASSWORD=$(sed -n 's/MONGO_INITDB_ROOT_PASSWORD=//p' .env)
[[ -z "${DOMAIN}" ]] && export DOMAIN=$(sed -n 's/DOMAIN=//p' .env)

export PYTHONPATH=$PYTHONPATH:$(pwd)/app
echo "${C_BLUE}INFO:${C_RESET}    Setup complete"
cd "$CURRENTDIR"
