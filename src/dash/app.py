# -*- coding: utf-8 -*-

"""Module to create Flask and Dash applications."""

from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc

from common.config import Config
from common.mongo import Mongo


def create_flask():
    """Create the Flask instance for this application.

    Returns:
        flask.Flask: flask application
    """
    server = Flask(__package__)

    # load default settings
    server.config.from_object(Config)

    return server


def create_dash(server):
    """Create the Dash instance for this application.

    Args:
        server (flask.Flask): flask application
    Returns:
        dash.Dash: dash application
    """
    app = Dash(
        name=__package__,
        server=server,
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.LUX],
    )

    # Initialise logging
    Config.init_logging(app.logger)
    server.logger.removeHandler(app.logger.handlers[0])

    # Initialise the mongo database
    app.mongo = Mongo.connect(app.logger, app.server.config["MONGO_URI"])

    # Update the Flask config a default "TITLE" and then with any new Dash
    # configuration parameters that might have been updated so that we can
    # access Dash config easily from anywhere in the project with Flask's
    # 'current_app'
    server.config.setdefault("TITLE", "Dash")

    # Set the app name
    app.title = "thetrains"

    return app


# Create the Flask instance
server = create_flask()

# Create the Dash instance
app = create_dash(server)
