# -*- coding: utf-8 -*-

"""Implements the thetrains graph network generation."""

import sys
import signal
import time
import logging
import functools

import networkx as nx
from decouple import config

from common.config import config_dict
from common.mongo import Mongo


log = logging.getLogger("graph_generator")


def timer(func):
    """Print the runtime of the decorated function."""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        return_value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        log.debug(f"Completed {func.__name__!r} in {run_time:.4f} secs")
        return return_value

    return wrapper_timer


class GraphGenerator(object):
    """Graph generator class to approximate train network locations."""

    def __init__(self, log, mongo, k, iterations):
        """Initialise GraphGenerator.

        Args:
            log (logging.logger): Logger to use
            mongo (common.mongo.Mongo): Database class
            k (float): Spring layout k coefficient
            iterations (int): Spring layout iterations
        """
        self.log = log
        self.mongo = mongo
        self.k = k
        self.iterations = iterations
        self.log.debug("k: {}, iterations: {}".format(self.k, self.iterations))

    def run(self):
        """Build, tidy, and layout the graph."""
        self.log.info("Starting graph generation at {}".format(time.ctime()))
        if not self.get_berths():
            return
        if not self.clean_nodes():
            return
        if not self.run_layout():
            return
        if not self.update_berths():
            return
        self.log.info("Graph generation completed at {}".format(time.ctime()))

    @timer
    def get_berths(self):
        """Generate the initial graph from the berths stored in the database."""
        self.graph = nx.Graph()  # Create a new empty graph

        # Get the berths from the database
        try:
            berths = self.mongo.get("BERTHS")
            if berths is None:
                return False
        except Exception as e:
            self.log.error("Could not get berths from database, {}".format(e))
            return False

        # Loop through all berths and add nodes and edges to the graph
        for berth in berths:
            if "FIXED" in list(berth.keys()):
                self.graph.add_node(
                    berth["NAME"],
                    lon=berth["LONGITUDE"] * 100000,
                    lat=berth["LATITUDE"] * 100000,
                    fixed=True,
                )
            else:
                self.graph.add_node(berth["NAME"], lon=None, lat=None, fixed=False)

            if "CONNECTIONS" in list(berth.keys()):
                for connected_berth in berth["CONNECTIONS"]:
                    self.graph.add_edge(berth["NAME"], connected_berth, weight=1.0)

        self.log.debug("Nodes from db {}".format(len(self.graph.nodes)))

        return True

    @timer
    def clean_nodes(self):
        """Remove all nodes that should not be considered when calculating the layout."""
        # Remove all isolated nodes from the graph
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))

        # Just select nodes that lie between fixed nodes
        known = dict(
            (n, d["fixed"]) for n, d in self.graph.nodes().items() if d["fixed"] is True
        )
        c_score = nx.algorithms.betweenness_centrality_subset(
            self.graph, list(known.keys()), list(known.keys())
        )
        nodes_between = [x for x in c_score if c_score[x] != 0.0]
        nodes_between.extend(list(known.keys()))  # Add on fixed nodes

        self.graph = self.graph.subgraph(nodes_between)
        self.log.debug(
            "Nodes remaining after cleaning {}".format(len(self.graph.nodes))
        )
        return True

    @timer
    def run_layout(self):
        """Run the spring layout that positions all the nodes."""
        # Run the spring layout algorithm on the network
        known_dict = dict(
            (n, [d["lat"], d["lon"]])
            for n, d in self.graph.nodes().items()
            if d["fixed"] is True
        )

        self.log.debug("There are {} fixed nodes".format(len(known_dict)))

        try:
            node_positions = nx.spring_layout(
                self.graph,
                k=self.k,
                pos=known_dict,
                fixed=known_dict.keys(),
                iterations=self.iterations,
            )
        except Exception as e:
            self.log.error("Could not calculate layout, {}".format(e))
            return False

        for node, position in node_positions.items():
            self.graph.nodes[node]["lat"] = position[0] / 100000
            self.graph.nodes[node]["lon"] = position[1] / 100000

        return True

    @timer
    def update_berths(self):
        """Update the berth positions in the database."""
        for node, data in self.graph.nodes(data=True):
            update = {
                "$set": {
                    "LONGITUDE": data["lon"],
                    "LATITUDE": data["lat"],
                    "SELECTED": True,
                }
            }
            self.mongo.update("BERTHS", {"NAME": node}, update)

        self.graph = None  # Remove graph from memory
        return True


def exit_handler(sig, frame):
    """Exit method."""
    log.info("Exit signal handler invoked({})".format(sig))
    sys.exit(0)


def main():
    """Call when graph_generator starts."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    # Setup the configuration and mongo connection
    conf = config_dict[config("ENV", cast=str, default="local")]
    conf.init_logging(log)
    mongo = Mongo(log, conf.MG_URI)

    # Create the graph generator
    gen = GraphGenerator(log, mongo, conf.GRAPH_K, conf.GRAPH_ITERATIONS)

    # Run the graph generator in a loop, run every GRAPH_UPDATE_RATE seconds
    while 1:
        gen.run()
        time.sleep(conf.GRAPH_UPDATE_RATE)


if __name__ == "__main__":
    main()
