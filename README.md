# thetrains

[![Website](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://thetrains.co.uk/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A project to gather, explore, analyse and present train related data collected primarily from the [Network Rail feeds](https://wiki.openraildata.com/index.php?title=Main_Page). Currently, a graphical representation of the UK rail network is generated from raw train movement data and presented using a [Dash](https://plotly.com/dash/) application. The live dashboard for this project is located at
[thetrains.co.uk](https://thetrains.co.uk/).

The full deployment consists of four containers:

1. mongo - MongoDB database instance to persist all data
2. collector - Constantly gathers a large volume of raw train movement data from
   the Network Rail feeds for storage in the MongoDB instance.
3. generator - Cleans and processes raw train movement data to generate a novel
   graphical representation of the U.K rail network. A Fruchterman-Reingold
   force-directed algorithm is used for position estimation.
4. dash - Dash frontend application to display the generated graphical network
   alongside live network usage.

The [wiki](https://github.com/joshtingey/the-trains/wiki) contains information on the projects inner workings.

## Develop locally with docker-compose

First, a .env file containing all the required environment variables is needed. See .env.example for an example. It is recommended to modify this file and rename it to .env. To build and run all the containers locally run:

```bash
make build
```

You can then view the dash application at localhost:8000. To stop all the containers run:

```bash
make down
```

## Deploy to Kubernetes cluster

First, the ./k8s/setup.yaml file needs to be modified for your cluster setup. Additionally, You will need both kubectl and [skaffold](https://skaffold.dev/) for deployment.

To run the initial cluster setup run:

```bash
make k8s_setup
```

This step sets up the namespace, configuration, certificates, the application service and ingress. To build and push the containers to the GitHub container repository and then deploy to the cluster run:

```bash
make k8s_deploy
```

To continuously build and deploy to the cluster while you make changes run:

```bash
skaffold dev
```

## Running the tests

The tests and other checking is run within a docker container, use by running:

```bash
make test
```