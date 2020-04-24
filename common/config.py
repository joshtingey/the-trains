# -*- coding: utf-8 -*-

"""
This module contains the configuration classes for the different deployment
cases for thetrains app. All configs derived from the base 'Config' class.
"""

import logging

from decouple import config

from common.logging import client_logger


class Config(object):
    """
    Base config class with all common configuration variables and methods.
    """
    MG_USER = config(
        'MONGO_INITDB_ROOT_USERNAME', default="mongo_username"
    )
    MG_PASS = config(
        'MONGO_INITDB_ROOT_PASSWORD', default="mongo_password"
    )

    MAPBOX_TOKEN = config('MAPBOX_TOKEN')
    CONN_ATTEMPTS = config('CONN_ATTEMPTS', cast=int, default=5)
    PPM_FEED = config('PPM_FEED', cast=bool, default=False)
    TD_FEED = config('TD_FEED', cast=bool, default=False)

    @staticmethod
    def init_logging(log):
        """
        Initialise logging.

        Args:
            log (logging.logger): Logger to initialise
        """
        log_level = logging.getLevelName(config("LOG_LEVEL", default='INFO'))
        log.setLevel(log_level)
        client_logger.setLevel(log_level)
        log.addHandler(client_logger)


class LocalConfig(Config):
    """
    Configuration for use when natively running locally.
    """

    def __init__(self):
        """
        Initialise the LocalConfig.
        """
        super().__init__()

    MG_URI = 'mongodb://{}:{}@localhost:27017'.format(
        Config.MG_USER,
        Config.MG_PASS
    )
    NR_USER = config('NR_USER_DEV')
    NR_PASS = config('NR_PASS_DEV')


class DockerConfig(Config):
    """
    Configuration for use with running locally with docker.
    """

    def __init__(self):
        """
        Initialise the DockerConfig.
        """
        super().__init__()

    MG_URI = 'mongodb://{}:{}@mongo:27017'.format(
        Config.MG_USER,
        Config.MG_PASS
    )
    NR_USER = config('NR_USER_DEV')
    NR_PASS = config('NR_PASS_DEV')


class ProdConfig(Config):
    """
    Configuration for use when pushing to k8s production.
    """

    def __init__(self):
        """
        Initialise the ProdConfig.
        """
        super().__init__()

    MG_URI = 'mongodb://{}:{}@mongo:27017'.format(
        Config.MG_USER,
        Config.MG_PASS
    )
    NR_USER = config('NR_USER_PROD')
    NR_PASS = config('NR_PASS_PROD')


# Create a config dictionary which is used while initiating the application.
# Config that is going to be used will be specified in the .env file
config_dict = {
    'local': LocalConfig,
    'docker': DockerConfig,
    'prod': ProdConfig
}
