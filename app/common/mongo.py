# -*- coding: utf-8 -*-

"""Module to provide communication methods with the MongoDB database."""

from pymongo import MongoClient
import pandas as pd


class Mongo(object):
    """Class to handle MongoDB data flow."""

    def __init__(self, log, uri):
        """Initialise Mongo.

        Args:
            log (logging.logger): logger to use
            uri (str): MongoDB connection string
        """
        self.log = log  # We take the logger from the application
        self.client = None  # Mongo database
        try:
            client = MongoClient(uri)
            self.client = client.thetrains
            self.log.info("Connected to mongo at {}".format(uri))
        except Exception:
            self.log.warning("Mongo connection error for {}, continue".format(uri))
            self.client = None

    def drop(self, name):
        """Drop a named collection.

        Args:
            name (str): collection name
        """
        try:
            self.client.drop_collection(name)
        except Exception as e:
            self.log.warning("Mongo error ({})".format(e))

    def add(self, collection, doc):
        """Add a document to a collection.

        Args:
            collection (str): collection name
            doc (dict): document in dict format
        """
        try:
            self.client[collection].insert_one(doc)
        except Exception as e:
            self.log.warning("Mongo error ({})".format(e))

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
            self.log.warning("Mongo error ({})".format(e))

    def get(self, collection):
        """Get all documents from a collection.

        Args:
            collection (str): collection name
        """
        try:
            return self.client[collection].find()
        except Exception as e:
            self.log.warning("Mongo error ({})".format(e))
            return None

    def get_ppm_df(self):
        """Get a pandas dataframe containing all PPM data.

        Returns:
            pd.DataFrame: PPM Pandas dataframe
        """
        ppm_dict = {
            "date": [],
            "total": [],
            "on_time": [],
            "late": [],
            "ppm": [],
            "rolling_ppm": [],
        }

        docs = self.get("ppm")
        if docs is None:
            return None

        for doc in self.get("ppm"):
            ppm_dict["date"].append(doc["date"])
            ppm_dict["total"].append(doc["total"])
            ppm_dict["on_time"].append(doc["on_time"])
            ppm_dict["late"].append(doc["late"])
            ppm_dict["ppm"].append(doc["ppm"])
            ppm_dict["rolling_ppm"].append(doc["rolling_ppm"])

        df = pd.DataFrame.from_dict(ppm_dict)
        return df

    def get_berths(self):
        """Get the nodes and edges of the graph as dataframes.

        Returns:
            pd.DataFrame: nodes dataframe
            pd.DataFrame: edges dataframe
        """
        berths = self.get("BERTHS")
        selected = {}
        for b in berths:
            if "SELECTED" in list(b.keys()):
                if b["SELECTED"]:
                    selected[b["NAME"]] = b

        lat, lon = [], []
        for name, data in selected.items():
            if "CONNECTIONS" in list(data.keys()):
                for connection in data["CONNECTIONS"]:
                    if connection in selected:
                        lat.append(data["LATITUDE"])
                        lat.append(selected[connection]["LATITUDE"])
                        lat.append(None)
                        lon.append(data["LONGITUDE"])
                        lon.append(selected[connection]["LONGITUDE"])
                        lon.append(None)

        nodes = pd.DataFrame.from_dict(selected, orient="index")
        nodes["FIXED"].fillna(False, inplace=True)
        edges = pd.DataFrame({"LATITUDE": lat, "LONGITUDE": lon})
        return nodes, edges
