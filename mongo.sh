#! /bin/bash

echo "Deploying..."

read_var() {
    VAR=$(grep $1 $2 | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo ${VAR[1]}
}

MONGO_INITDB_ROOT_USERNAME=$(read_var MONGO_INITDB_ROOT_USERNAME .env)
MONGO_INITDB_ROOT_PASSWORD=$(read_var MONGO_INITDB_ROOT_PASSWORD .env)

echo "Using MONGO_INITDB_ROOT_USERNAME: $MONGO_INITDB_ROOT_USERNAME"
echo "Using MONGO_INITDB_ROOT_PASSWORD: $MONGO_INITDB_ROOT_PASSWORD"

docker run -d -p 27017:27017 -v the-trains_thetrains_mongo:/data/db \
    -e MONGO_INITDB_ROOT_USERNAME="$MONGO_INITDB_ROOT_USERNAME" \
    -e MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
    --name mongo mongo:latest

echo "DONE!"
