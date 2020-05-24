# -*- coding: utf-8 -*-

import logging
import json

import networkx as nx
import pandas as pd

from common.config import config_dict
from common.mongo import Mongo


class Graph(object):
    """
    Graph class for mapping the train network.
    """

    def __init__(self, log, mongo):
        """
        Initialise Graph.

        Args:
            log (logging.logger): Logger to use
            mongo (common.mongo.Mongo): Database class
        """
        self.log = log
        self.mongo = mongo
        self.graph = nx.Graph()  # Create the empty graph

        # Load the known STANOX locations into memory
        locations_file = open('./thetrains/locations.json')
        self.locations = json.load(locations_file)
        locations_file.close()

        self.build()  # Build the graph

    def __repr__(self):
        """
        Graph string representation.

        Returns:
            str: string detailing the train network graph
        """
        return 'Train network graph with {} nodes and {} edges.'.format(
            len(self.graph.nodes), len(self.graph.edges))

    def build(self):
        """
        Build the graph from the database.
        """
        for td in self.mongo.get("td"):
            self.graph.add_edge(td["from"], td["to"], weight=1.0)

        # Fix nodes with known locations
        fixed_nodes = {}
        for node in self.graph.nodes:
            if node in self.locations:
                self.graph.nodes[node]['fixed'] = True
                self.graph.nodes[node]['lat'] = self.locations[node]['LAT']
                self.graph.nodes[node]['lon'] = self.locations[node]['LON']
                fixed_nodes[node] = [
                    self.locations[node]['LAT'],
                    self.locations[node]['LON']
                ]
            else:
                self.graph.nodes[node]['fixed'] = False

        # Run the spring layout algorithm on the network
        node_positions = nx.spring_layout(
            self.graph, k=0.0001,
            pos=fixed_nodes,
            fixed=fixed_nodes.keys()
        )
        for node, position in node_positions.items():
            self.graph.nodes[node]['lat'] = position[0]
            self.graph.nodes[node]['lon'] = position[1]

    @property
    def nodes(self):
        """
        Get the graph nodes.

        Returns:
            pd.DataFrame: DataFrame of node date
        """
        names, lat, lon = [], [], []
        for node in self.graph.nodes():
            names.append(node)
            lat.append(self.graph.nodes[node]['lat'])
            lon.append(self.graph.nodes[node]['lon'])
        return pd.DataFrame({'name': names, 'lat': lat, 'lon': lon})

    @property
    def edges(self):
        """
        Get the edge positions.

        Returns:
            pd.DataFrame: DataFrame of lon and lat edge positions
        """
        lat, lon = [], []
        for edge in self.graph.edges():
            lat.append(self.graph.nodes[edge[0]]['lat'])
            lat.append(self.graph.nodes[edge[1]]['lat'])
            lat.append(None)
            lon.append(self.graph.nodes[edge[0]]['lon'])
            lon.append(self.graph.nodes[edge[1]]['lon'])
            lon.append(None)
        return pd.DataFrame({'lat': lat, 'lon': lon})


def main():
    """
    Main function called when graph is run standalone.
    """
    log = logging.getLogger("graph")

    conf = config_dict['local']
    conf.init_logging(log)
    mongo = Mongo(log, conf.MG_URI)

    graph = Graph(log, mongo)
    print(graph)


if __name__ == '__main__':
    main()
