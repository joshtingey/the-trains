"""This is where we defined the Config files, which are used for initiating the
application with specific settings such as logger configurations or different
database setups."""

import logging

from decouple import config

from common.logging import file_logger, client_logger


class LocalConfig:
    """Initialise a configuration for use when locally running apps"""

    MG_USER = config(
        'MONGO_INITDB_ROOT_USERNAME', default="mongo_user"
    )
    MG_PASS = config(
        'MONGO_INITDB_ROOT_PASSWORD', default="mongo_pass"
    )
    MG_HOST = config(
        'MONGO_HOST', default="localhost"
    )
    MG_PORT = config(
        'MONGO_PORT', default="27017"
    )
    MG_URI = 'mongodb://{}:{}@{}:{}'.format(
        MG_USER, MG_PASS, MG_HOST, MG_PORT
    )

    NR_USER = config('NR_USER')
    NR_PASS = config('NR_PASS')
    MAPBOX_TOKEN = config('MAPBOX_TOKEN')

    CONN_ATTEMPTS = config('CONN_ATTEMPTS', cast=int, default=5)
    PPM_FEED = config('PPM_FEED', cast=bool, default=False)
    TD_FEED = config('TD_FEED', cast=bool, default=False)

    @staticmethod
    def init_logging(log):
        """Initiates logging."""
        LOG_LEVEL = logging.getLevelName(config(
            "LOG_LEVEL", default='INFO'
        ))
        log.setLevel(LOG_LEVEL)
        file_logger.setLevel(LOG_LEVEL)
        log.addHandler(file_logger)
        client_logger.setLevel(LOG_LEVEL)
        log.addHandler(client_logger)


class DockerConfig:
    """Initialise a configuration for use with docker"""

    MG_USER = config(
        'MONGO_INITDB_ROOT_USERNAME', default="mongo_user"
    )
    MG_PASS = config(
        'MONGO_INITDB_ROOT_PASSWORD', default="mongo_pass"
    )
    MG_URI = 'mongodb://{}:{}@mongo:27017'.format(
        MG_USER, MG_PASS
    )

    NR_USER = config('NR_USER')
    NR_PASS = config('NR_PASS')
    MAPBOX_TOKEN = config('MAPBOX_TOKEN')

    CONN_ATTEMPTS = config('CONN_ATTEMPTS', cast=int, default=5)
    PPM_FEED = config('PPM_FEED', cast=bool, default=False)
    TD_FEED = config('TD_FEED', cast=bool, default=False)

    @staticmethod
    def init_logging(log):
        """Initiates logging."""
        LOG_LEVEL = logging.getLevelName(config(
            "LOG_LEVEL", default='INFO'
        ))
        log.setLevel(LOG_LEVEL)
        file_logger.setLevel(LOG_LEVEL)
        log.addHandler(file_logger)
        client_logger.setLevel(LOG_LEVEL)
        log.addHandler(client_logger)


# Create a config dictionary which is used while initiating the application.
# Config that is going to be used will be specified in the .env file
config_dict = {
    'local': LocalConfig,
    'docker': DockerConfig,
}
