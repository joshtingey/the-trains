"""This module provides all the methods to communicate with the databases.
We definie a base database class which other specific database classes
derive from. This abstracts away the mechanics of the database from the
rest of the source code"""

from pymongo import MongoClient
import pandas as pd


class Mongo(object):
    """Class to handle MongoDB data flow"""
    def __init__(self, log, uri):
        self.log = log  # We take the logger from the application
        self.client = None  # Mongo database
        self.init(uri)

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

    def drop(self, name):
        self.client.drop_collection(name)

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

    def get_ppm_df(self):
        ppm_dict = {
            'date': [],
            'total': [],
            'on_time': [],
            'late': [],
            'ppm': [],
            'rolling_ppm': []
        }

        for doc in self.get("ppm"):
            ppm_dict['date'].append(doc['date'])
            ppm_dict['total'].append(doc['total'])
            ppm_dict['on_time'].append(doc['on_time'])
            ppm_dict['late'].append(doc['late'])
            ppm_dict['ppm'].append(doc['ppm'])
            ppm_dict['rolling_ppm'].append(doc['rolling_ppm'])

        df = pd.DataFrame.from_dict(ppm_dict)
        return df
