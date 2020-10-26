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
    GENERATOR_RATE = config("GENERATOR_RATE", cast=int, default=3600)
    GENERATOR_K = config("GENERATOR_K", cast=float, default=0.000001)
    GENERATOR_ITER = config("GENERATOR_ITER", cast=int, default=5000)
    GENERATOR_CUT_D = config("GENERATOR_CUT_D", cast=float, default=0.25)
    GENERATOR_SCALE = config("GENERATOR_SCALE", cast=int, default=100000)
    GENERATOR_DELTA_B = config("GENERATOR_DELTA_B", cast=int, default=5)
    GENERATOR_DELTA_T = config("GENERATOR_DELTA_T", cast=int, default=1)

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
