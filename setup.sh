#! /bin/bash

CURRENTDIR=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

if [ -d "thetrains_env/" ]
then
    source thetrains_env/bin/activate
else
    sudo apt install python3-dev python3-pip python3-venv
    python3 -m venv thetrains_env
    source thetrains_env/bin/activate

    pip install -r common/requirements.txt
    pip install -r dash/requirements.txt
    pip install -r collector/requirements.txt
fi

# To make tests pass we export dummy deployment environment variables
export K8S_SERVER='dummy'
export K8S_CERTIFICATE='dummy'
export K8S_TOKEN='dummy'

export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "thetrains env setup"
cd $CURRENTDIR  # Go back to the user directory

