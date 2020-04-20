# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import networkx as nx


class Network(object):
    """Network class for mapping the train network."""
    def __init__(self, log, mongo):
        self.log = log
        self.mongo = mongo

    def run(self):
        """Run the network generation."""
        G = nx.Graph()

        for movement in self.mongo.get("tm"):
            G.add_edge(movement["from"], movement["to"])

        nx.draw_spring(G, with_labels=True, font_weight='bold')
        plt.show()
