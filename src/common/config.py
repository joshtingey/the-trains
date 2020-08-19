# -*- coding: utf-8 -*-

"""Module containing configuration classes for the different deployment cases."""

import logging

from decouple import config

from common.logging import client_logger


class Config(object):
    """Base config class with all common configuration variables and methods."""

    # Mongo DB configuration
    MONGO_USER = config("MONGO_INITDB_ROOT_USERNAME", default="user")
    MONGO_PASS = config("MONGO_INITDB_ROOT_PASSWORD", default="pass")
    MONGO_URI = "mongodb://{}:{}@mongo:27017".format(MONGO_USER, MONGO_PASS)

    # Collector configuration
    COLLECTOR_NR_USER = config("COLLECTOR_NR_USER", default="user")
    COLLECTOR_NR_PASS = config("COLLECTOR_NR_PASS", default="pass")
    COLLECTOR_ATTEMPTS = config("COLLECTOR_ATTEMPTS", cast=int, default=5)
    COLLECTOR_PPM = config("COLLECTOR_PPM", cast=bool, default=False)
    COLLECTOR_TD = config("COLLECTOR_TD", cast=bool, default=False)
    COLLECTOR_TM = config("COLLECTOR_TM", cast=bool, default=False)

    # Generator configuration
    GENERATOR_UPDATE_RATE = config("GENERATOR_UPDATE_RATE", cast=int, default=3600)
    GENERATOR_K = config("GENERATOR_K", cast=float, default=0.0001)
    GENERATOR_ITERATIONS = config("GENERATOR_ITERATIONS", cast=int, default=5000)

    # Dash configuration
    DASH_MAPBOX_TOKEN = config("DASH_MAPBOX_TOKEN", default="token")

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