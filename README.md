# thetrains

A personal project to produce a web based dash(flask) application to display results from train related data analysis.

## Develop locally with docker-compose

Create an .env file and set the following variables...

- ENV  # Which env are you using (local or docker)
- LOG_LEVEL  # logging verbosity level 
- FILE_LOG=False  # Should we log to file
- MONGO_INITDB_ROOT_USERNAME  # MongoDB default username
- MONGO_INITDB_ROOT_PASSWORD  # MongoDB default password
- NR_USER  # Network rail feed username
- NR_PASS  # Network rail feed password
- MAPBOX_TOKEN  # Mapbox account token
- CONN_ATTEMPTS  # Number of STOMP connection attempts to make (suggested=5)
- PPM_FEED  # Should we collect the PPM feed data
- TD_FEED  # Should we collect the TD feed data

To start all the containers run...

```bash
$ make dev
```

You can then view the dash application at localhost:8000. To then stop all the container run...

```bash
$ make down
```

## Deploy locally with docker-compose

To start a production deployment locally with an nginx reverse proxy and certificates cofigured run...

```bash
$ make prod
```

You can then view the dash application at localhost:80. To then stop all the container run...

```bash
$ make down
```

## Deploy to Kubernetes Cluster

To build and push the containers to the container repository run...

```bash
$ skaffold build
```

To deploy everything run...

```bash
$ source scripts/deploy.sh
```

To continuously build and deploy to the cluster while you make changes run...

```bash
$ skaffold dev
```

## Checking the mongodb database

```bash
$ mongo --username mongo_db_user --password mongo_db_pass --authenticationDatabase admin
$ use thetrains
$ db.BERTHS.find()
```