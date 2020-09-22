# thetrains

[![Website](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://thetrains.co.uk/)
[![Pipeline](https://gitlab.com/JoshTingey/the-trains/badges/master/pipeline.svg)](https://gitlab.com/JoshTingey/the-trains/pipelines)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A personal project to gather, explore, analyse and present train-related data collected primarily from the [Network Rail data feeds](https://wiki.openraildata.com/index.php?title=Main_Page). Furthermore, a `graph' of the UK rail network is generated and then presented using a [Dash](https://plotly.com/dash/)([Flask](https://flask.palletsprojects.com/en/1.1.x/)) application. The live website for this project is at [thetrains.co.uk](https://thetrains.co.uk/).

Currently, the deployment consists of 4 containers:

1. mongo - MongoDB database to persist all data
2. collector - Gathers data from the Network Rail data feeds
3. generator - Generates a UK rail network 'graph' from berth-level data and runs Fruchterman-Reingold force-directed algorithm for position estimation
4. dash - Dash application frontend to display the generated graph and other analysis

The [wiki](https://github.com/joshtingey/the-trains/wiki) contains detailed information on the projects inner workings.

All code is replicated across both a [github](https://github.com/joshtingey/the-trains) and [gitlab](https://gitlab.com/JoshTingey/the-trains) repository with the later being used to run the ci/cd pipeline.

## Develop locally with docker-compose

First, a .env file containing all the required environment variables is needed. See .env.example for an example, it is recommended to modify this and rename to .env. Then to start all the containers locally run...

```bash
make up
```

You can then view the dash application at localhost:8000. To then stop all the containers run...

```bash
make down
```

## Deploy to Kubernetes cluster

First, the ./k8s/setup.yaml file needs to be modified for the cluster setup. Additionally, You will need both kubectl and [skaffold](https://skaffold.dev/) for this.

To run the initial cluster setup run...

```bash
make k8s
```

This sets up the namespace, configuration, certificates and the application service and ingress.
To build and push the containers to the container repository and then deploy to the cluster run...

```bash
make deploy
```

To continuously build and deploy to the cluster while you make changes run...

```bash
skaffold dev
```

## Running the tests

The tests and other checking is run within a docker container, use by running...

```bash
make test
```

You can also use 'black' on the code by running...

```bash
make black
```