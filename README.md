# thetrains

[![Pipeline](https://gitlab.com/JoshTingey/the-trains/badges/master/pipeline.svg)](https://gitlab.com/JoshTingey/the-trains/pipelines) [![Website](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://thetrains.co.uk/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/94593ef8ea534d63912e073584a91932)](https://www.codacy.com/manual/joshtingey93/the-trains?utm_source=gitlab.com&amp;utm_medium=referral&amp;utm_content=JoshTingey/the-trains&amp;utm_campaign=Badge_Grade)

A personal project to produce a web based dash(flask) application to display the results of train related data analysis. The website for this code is at [https://thetrains.co.uk/](https://thetrains.co.uk/). 

Currently the deployment consists of 4 containers...
1.  MongoDB database - persists all data
2.  Data collector - collects data from the Network Rail data feeds
3.  Graph generator - creates rail network 'graph' from berth-level data and runs Fruchterman-Reingold force-directed algorithm for positions
4.  Dash app - dash application frontend to display the graph etc...

## Develop locally with docker-compose

First a .env file is required, see below. Then to start all the containers run...

```bash
make up
```

You can then view the dash application at localhost:8000. To then stop all the container run...

```bash
make down
```

## Deploy to Kubernetes Cluster

First the ./k8s/setup.yaml file needs to be modified for the cluster setup. You will need both
kubectl and [skaffold](https://skaffold.dev/) for this.

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

## Environment variables

An .env file is required with the following variables...

| Variable name              | Type | Description                                 |
| -------------------------- | ---- | ------------------------------------------- |
| LOG_LEVEL                  | str  | logging verbosity level (DEBUG, INFO)       |
| MONGO_INITDB_ROOT_USERNAME | str  | MongoDB username                            |
| MONGO_INITDB_ROOT_PASSWORD | str  | MongoDB password                            |
| COLLECTOR_NR_USER          | str  | Network rail feed username                  |
| COLLECTOR_NR_PASS          | str  | Network rail feed password                  |
| DASH_MAPBOX_TOKEN          | str  | Mapbox account token                        |
| COLLECTOR_ATTEMPTS         | int  | Number of STOMP connection attempts to make |
| COLLECTOR_PPM              | bool | Should PPM feed data be collected           |
| COLLECTOR_TD               | bool | Should TD feed data be collected            |
| COLLECTOR_TM               | bool | Should TM feed data be collected            |
| GENERATOR_UPDATE_RATE      | int  | Update rate of network graph in seconds     |
| GENERATOR_K                | int  | Layout k coefficient for graph generation   |
| GENERATOR_ITERATIONS       | int  | Layout iterations for graph generation      |

See .env.example for an example

## Checking the mongodb database

```bash
mongo --username <MONGO_INITDB_ROOT_USERNAME> --password <MONGO_INITDB_ROOT_PASSWORD> --authenticationDatabase admin
use thetrains
db.BERTHS.find()  # To display all BERTH documents
```