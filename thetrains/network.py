# -*- coding: utf-8 -*-

import logging

import networkx as nx

from common.config import config_dict
from common.mongo import Mongo


class Network(object):
    """
    Network class for mapping the train network.
    """

    def __init__(self, log, mongo):
        """
        Initialise Network.

        Args:
            log (logging.logger): Logger to use
            mongo (common.mongo.Mongo): Database class
        """
        self.log = log
        self.mongo = mongo

    def get_positions(self):
        """
        Run the network generation.

        Returns:
            positions dictionary
        """
        G = nx.Graph()
        for movement in self.mongo.get("td"):
            G.add_edge(movement["from"], movement["to"])

        positions = nx.spring_layout(G)

        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = positions[node]
            node_x.append(x)
            node_y.append(y)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = positions[edge[0]]
            x1, y1 = positions[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        pos_dict = {
            'names': G.nodes,
            'node_x': node_x,
            'node_y': node_y,
            'edge_x': edge_x,
            'edge_y': edge_y,
        }

        return pos_dict


def main():
    """
    Main function called when network is run standalone.
    """
    log = logging.getLogger("network")

    conf = config_dict['local']
    conf.init_logging(log)
    mongo = Mongo(log, conf)

    network = Network(log, mongo)
    network.run()


if __name__ == '__main__':
    main()
