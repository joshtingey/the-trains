# thetrains

A personal project to produce a web based dash(flask) application to display results from train related data analysis.

## Run Locally with docker-compose

You need to define the following variables in an .env file and also 'export' them...

- DB_USER
- DB_PASS
- DB_NAME
- NR_USER
- NR_PASS

To start all the containers run...

```
$ make up
```

You can then view the dash application at localhost:80. To then stop all the container run...

```
$ make down
```

You can also cleanup all the local containers/images using

```
$ make clean
```

## Deploy to Kubernetes Cluster

To build and push the containers to the container repository run...

```
$ skaffold build
```

To deploy everything run...

```
$ source scripts/deploy.sh
```

To continuously build and deploy to the cluster while you make changes run...

```
$ skaffold dev
```

## Connect to postgres

First forward the postgres container port to your local machine...

```
$ kubectl port-forward service/postgres 5432:5432 -n $DB_NAME
```

Then connect to the database using...

```
$ psql -h localhost -U $DB_USER --password -p 5432 $DB_NAME
```