# thetrains

A personal project to produce a web based dash(flask) application to display results from train related data analysis.

## Run Locally with docker-compose

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

## Deploy to thetrainskube Kubernetes Cluster with Skaffold

You must have kubectl setup to communicate with "thetrainskube" cluster and skaffold installed

To deploy the postgres database...

```
$ kubectl apply -f manifests/database
```

To build and deploy the app and collector run...

```
$ skaffold run
```

To continuously build and deploy to the cluster while you make changes run...

```
$ skaffold dev
```

To delete the app and collector from the cluster run...

```
$ skaffold delete
```

## Connect to postgres

First forward the postgres container port to your local machine...

```
$ kubectl port-forward service/postgres 5432:5432 -n thetrains
```

Then connect to the database using...

```
$ psql -h localhost -U thetrains --password -p 5432 thetrains-test
```