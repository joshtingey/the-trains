# -*- coding: utf-8 -*-

"""Implements the thetrains graph network generation."""

import sys
import signal
import time
import logging
import functools
import math

import networkx as nx

from common.config import Config
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
        log.info(f"Completed {func.__name__!r} in {run_time:.4f} secs")
        return return_value

    return wrapper_timer


class GraphGenerator(object):
    """Graph generator class to approximate train network locations."""

    def __init__(self, log, mongo, k, iterations, cut_distance):
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
        self.cut_distance = cut_distance
        self.log.info("k: {}, iterations: {}".format(self.k, self.iterations))

    def run(self):
        """Build, tidy, and layout the graph."""
        self.log.info("Starting graph generation at {}".format(time.ctime()))
        if not self.get_berths():
            return
        if not self.clean_graph():
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

        self.log.info("Nodes from db {}".format(len(self.graph.nodes)))

        return True

    def clean_graph(self):
        """Clean the graph to remove nodes/edges to not be considered in the layout."""
        self.remove_isolated_nodes()
        self.remove_duplicate_locations()
        self.remove_distant_nodes()
        self.remove_floating_nodes()
        self.log.info("Nodes remaining after cleaning {}".format(len(self.graph.nodes)))
        return True

    @timer
    def remove_isolated_nodes(self):
        """Remove isolated nodes from the graph."""
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))

    @timer
    def remove_duplicate_locations(self):
        """Combine fixed nodes that have the same location."""
        fixed = [n for n, d in self.graph.nodes().items() if d["fixed"] is True]
        combine = {}
        for base_node in fixed:
            combine[base_node] = []
            for other_node in fixed:
                if (
                    self.graph.nodes[base_node]["lon"]
                    == self.graph.nodes[other_node]["lon"]
                    and self.graph.nodes[base_node]["lat"]
                    == self.graph.nodes[other_node]["lat"]
                ):
                    combine[base_node].append(other_node)

        for base_node, combine_list in combine.items():
            for combine_node in combine_list:
                try:
                    lon = self.graph.nodes[base_node]["lon"]
                    lat = self.graph.nodes[base_node]["lat"]
                    self.graph = nx.contracted_nodes(
                        self.graph, base_node, combine_node, self_loops=False
                    )
                    self.graph.nodes[base_node]["fixed"] = True
                    self.graph.nodes[base_node]["lon"] = lon
                    self.graph.nodes[base_node]["lat"] = lat
                except Exception as e:
                    self.log.debug("Already passed {}".format(e))
                    pass

    @timer
    def remove_distant_nodes(self):
        """Remove linked fixed nodes that are distant from one another."""
        for edge in self.graph.edges:
            node_0 = self.graph.nodes[edge[0]]
            node_1 = self.graph.nodes[edge[1]]
            if node_0["fixed"] is True and node_1["fixed"] is True:
                distance = math.sqrt(
                    math.pow(node_0["lat"] - node_1["lat"], 2)
                    + math.pow(node_0["lon"] - node_1["lon"], 2)
                )
                if distance >= self.cut_distance:
                    # self.log.debug(distance)
                    self.graph.remove_edge(edge[0], edge[1])

    @timer
    def remove_floating_nodes(self):
        """Remove nodes that do not lie between fixed nodes."""
        known = [n for n, d in self.graph.nodes().items() if d["fixed"] is True]
        c_score = nx.algorithms.betweenness_centrality_subset(self.graph, known, known)
        nodes_between = [x for x in c_score if c_score[x] != 0.0]
        nodes_between.extend(known)  # Add on fixed nodes
        self.graph = self.graph.subgraph(nodes_between)

    @timer
    def run_layout(self):
        """Run the spring layout that positions all the nodes."""
        # Run the spring layout algorithm on the network
        known_dict = dict(
            (n, [d["lat"], d["lon"]])
            for n, d in self.graph.nodes().items()
            if d["fixed"] is True
        )

        self.log.info("There are {} fixed nodes".format(len(known_dict)))

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
    Config.init_logging(log)
    mongo = Mongo(log, Config.MONGO_URI)

    # Create the graph generator
    gen = GraphGenerator(
        log,
        mongo,
        Config.GENERATOR_K,
        Config.GENERATOR_ITERATIONS,
        Config.GENERATOR_CUT_DISTANCE,
    )

    # Run the graph generator in a loop, run every GRAPH_UPDATE_RATE seconds
    while 1:
        gen.run()
        time.sleep(Config.GENERATOR_UPDATE_RATE)


if __name__ == "__main__":
    main()
