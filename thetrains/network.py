# -*- coding: utf-8 -*-

import logging

import matplotlib.pyplot as plt
import networkx as nx

from common.config import config_dict
from common.mongo import Mongo


class Network(object):
    """Network class for mapping the train network."""
    def __init__(self, log, mongo):
        self.log = log
        self.mongo = mongo

    def run(self):
        """Run the network generation."""
        G = nx.Graph()

        for movement in self.mongo.get("td"):
            G.add_edge(movement["from"], movement["to"])

        nx.draw_spring(G, with_labels=True, font_weight='bold')
        plt.show()


def main():
    """Main function called when network is run standalone"""

    log = logging.getLogger("network")

    conf = config_dict['local']
    conf.init_logging(log)
    mongo = Mongo(log, conf)

    network = Network(log, mongo)
    network.run()


if __name__ == '__main__':
    main()
