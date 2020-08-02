# -*- coding: utf-8 -*-

"""Module containing configuration classes for the different deployment cases."""

import logging

from decouple import config

from common.logging import client_logger


class Config(object):
    """Base config class with all common configuration variables and methods."""

    # Mongo DB configuration
    MG_USER = config("MONGO_INITDB_ROOT_USERNAME", default="mongo_db_user")
    MG_PASS = config("MONGO_INITDB_ROOT_PASSWORD", default="mongo_db_pass")

    # Mapbox configuration
    MAPBOX_TOKEN = config("MAPBOX_TOKEN")

    # Data collector configuration
    CONN_ATTEMPTS = config("CONN_ATTEMPTS", cast=int, default=5)
    PPM_FEED = config("PPM_FEED", cast=bool, default=False)
    TD_FEED = config("TD_FEED", cast=bool, default=False)
    TM_FEED = config("TM_FEED", cast=bool, default=False)

    # Graph generator configuration
    GRAPH_UPDATE_RATE = config("GRAPH_UPDATE_RATE", cast=int, default=600)
    GRAPH_K = config("GRAPH_K", cast=float, default=0.0001)
    GRAPH_ITERATIONS = config("GRAPH_ITERATIONS", cast=int, default=1000)

    @staticmethod
    def init_logging(log):
        """Initialise logging.

        Args:
            log (logging.logger): logger to initialise
        """
        log_level = logging.getLevelName(config("LOG_LEVEL", default="INFO"))
        log.setLevel(log_level)
        client_logger.setLevel(log_level)
        log.addHandler(client_logger)


class LocalConfig(Config):
    """Configuration for use when natively running locally."""

    def __init__(self):
        """Initialise the LocalConfig."""
        super().__init__()

    MG_URI = "mongodb://{}:{}@localhost:27017".format(Config.MG_USER, Config.MG_PASS)
    NR_USER = config("NR_USER_DEV")
    NR_PASS = config("NR_PASS_DEV")


class DockerConfig(Config):
    """Configuration for use with running locally with docker."""

    def __init__(self):
        """Initialise the DockerConfig."""
        super().__init__()

    MG_URI = "mongodb://{}:{}@mongo:27017".format(Config.MG_USER, Config.MG_PASS)
    NR_USER = config("NR_USER_DEV")
    NR_PASS = config("NR_PASS_DEV")


class ProdConfig(Config):
    """Configuration for use when pushing to k8s production."""

    def __init__(self):
        """Initialise the ProdConfig."""
        super().__init__()

    MG_URI = "mongodb://{}:{}@mongo:27017".format(Config.MG_USER, Config.MG_PASS)
    NR_USER = config("NR_USER_PROD")
    NR_PASS = config("NR_PASS_PROD")


# Create a config dictionary which is used while initiating the application.
# Config that is going to be used will be specified in the .env file
config_dict = {"local": LocalConfig, "docker": DockerConfig, "prod": ProdConfig}
