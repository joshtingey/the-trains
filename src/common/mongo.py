# -*- coding: utf-8 -*-

"""Module to provide communication methods with the MongoDB database."""

from pymongo import MongoClient


class Mongo(object):
    """Class to handle MongoDB data flow."""

    def __init__(self, log, client):
        """Initialise Mongo.

        Args:
            log (logging.logger): logger to use
            client (pymongo.MongoClient): pymongo client
        """
        self.log = log  # We take the logger from the application
        self.client = client  # Mongo database

    @classmethod
    def connect(cls, log, uri):
        """Connect to database, return None if not possible"""
        try:
            client = MongoClient(uri)
            client = client.thetrains  # Using thetrains database
            log.info("Connected to mongo at {}".format(uri))
            return cls(log, client)
        except Exception:
            log.warning("Mongo connection error: {}".format(uri))
            return None

    def collections(self):
        """Return list of all database collections."""
        collections = None
        try:
            collections = self.client.list_collection_names()
        except Exception as e:
            self.log.warning("Mongo collections error ({})".format(e))
        return collections

    def drop(self, name):
        """Drop a named collection.

        Args:
            name (str): collection name
        """
        try:
            self.client.drop_collection(name)
        except Exception as e:
            self.log.warning("Mongo drop error ({})".format(e))

    def add(self, collection, doc):
        """Add a document to a collection.

        Args:
            collection (str): collection name
            doc (dict): document in dict format
        """
        try:
            self.client[collection].insert_one(doc)
        except Exception as e:
            self.log.warning("Mongo add error ({})".format(e))

    def update(self, collection, selection, update):
        """Update document in collection by selection.

        Args:
            collection (str): collection name
            selection (dict): document selection
            update (dict): document update
        """
        try:
            self.client[collection].update_one(selection, update, upsert=True)
        except Exception as e:
            self.log.warning("Mongo update error ({})".format(e))

    def get(self, collection):
        """Get all documents from a collection.

        Args:
            collection (str): collection name
        """
        try:
            return self.client[collection].find()
        except Exception as e:
            self.log.warning("Mongo get error ({})".format(e))
            return None
