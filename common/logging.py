# -*- coding: utf-8 -*-

"""Module to setup logging with client handler.

The log level is defined in the .env file. The handler is
attached to all module/app loggers at initialisation.
"""

import sys
from logging import StreamHandler
import logging

# Logger setup
# Configure logger format
log_fmt = "[%(name)s] [%(threadName)s] [%(asctime)s] " "[%(levelname)s] %(message)s"

logger_formatter = logging.Formatter(log_fmt)

# Set up stream handler for client output
client_logger = StreamHandler(sys.stdout)
client_logger.setFormatter(logger_formatter)
