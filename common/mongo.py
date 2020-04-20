"""This module provides all the methods to communicate with the databases.
We definie a base database class which other specific database classes
derive from. This abstracts away the mechanics of the database from the
rest of the source code"""

from pymongo import MongoClient


class Mongo(object):
    """Class to handle MongoDB data flow"""
    def __init__(self, log, config):
        self.log = log  # We take the logger from the application
        self.client = None  # Mongo database
        self.init(config.MG_URI)

    def init(self, uri):
        """Initialise the MongoDB connection"""
        try:
            client = MongoClient(uri)
            self.client = client.thetrains
            self.log.info("Connected to mongo at {}".format(uri))
        except Exception:
            self.log.warning(
                "Mongo connection error for {}, continue".format(uri)
            )
            self.client = None

    def drop_all(self):
        names = self.mongo.get_collections()
        for col in names:
            self.mongo[col].drop()

    def add(self, collection, doc):
        """Add a document to a collection"""
        try:
            self.client[collection].insert_one(doc)
        except Exception as e:
            self.log.warning("Mongo error ({})".format(e))

    def get(self, collection):
        """Get all documents from a collection"""
        try:
            return self.client[collection].find()
        except Exception as e:
            self.log.warning("Mongo error ({})".format(e))
            return None
