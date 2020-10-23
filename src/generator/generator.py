# -*- coding: utf-8 -*-

"""Implements the thetrains graph network generation."""

import sys
import signal
import time
import logging
import functools
import math
import datetime

import pandas as pd
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
            cut_distance (float): Cut distance for cutting long distance connections
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
        try:
            # Get the BERTHS from the database
            berths = {berth["NAME"]: berth for berth in self.mongo.get("BERTHS")}
            if berths is None:
                return False
        except Exception as e:
            self.log.error("Could not get BERTHS from database, {}".format(e))
            return False

        try:
            # Get the TRAINS from the database
            trains = self.mongo.get("TRAINS")
            if trains is None:
                return False
        except Exception as e:
            self.log.error("Could not get TRAINS from database, {}".format(e))
            return False

        self.graph = nx.Graph()
        for train in trains:
            # Create and tidy the dataframe
            t = pd.DataFrame(train)
            t = t.drop(["_id", "NAME"], axis=1)

            # Check BERTHS and remove ones we don't want to use...
            t = t[
                t["BERTHS"].str.len() == 6
            ]  # Check berth name length is equal to 6 characters
            # Remove `STrike IN' berths
            t = t[~t["BERTHS"].str.endswith("STIN")]
            # Remove `Clear OUT' berths
            t = t[~t["BERTHS"].str.endswith("COUT")]
            # Remove current date berths
            t = t[~t["BERTHS"].str.endswith("DATE")]
            # Remove current time berths
            t = t[~t["BERTHS"].str.endswith("TIME")]
            # Remove current clock berths
            t = t[~t["BERTHS"].str.endswith("CLCK")]
            # Remove `Last Sent' berths
            t = t[~t["BERTHS"].str.slice(start=2, stop=4).str.contains("LS")]
            t = t[~t["BERTHS"].str.endswith("LS")]  # Remove `Last Sent' berths
            # Remove `Train Reporting' link status berths
            t = t[~t["BERTHS"].str.slice(start=2, stop=4).str.contains("TR")]
            # Remove SMART link status berths
            t = t[~t["BERTHS"].str.slice(start=2, stop=5).str.contains("SMT")]

            # Calculate the delta times between berths...
            t["DELTAS"] = t["TIMES"] - t["TIMES"].shift()

            # Remove first berth as we have no context to make a decision about it...
            t = t.iloc[1:]

            # Assuming that the real TD berth is always reported first, we can get rid
            # of all duplicate/fringe/waiting berths. Should probably uodate this as it
            # is most likely not always the case, so need to check other same timed
            # berths and use the most appropriate one, from the last three digits.
            delta_berth_time = 5
            t = t[t["DELTAS"] >= datetime.timedelta(seconds=delta_berth_time)]
            t = t.reset_index()

            # Remove duplicates of berths next to each other if exist
            t = t.loc[t["BERTHS"].shift(-1) != t["BERTHS"]]

            # Split the full train dataframe when there are large differences in time
            delta_train_time = 1
            splits = t.index[
                t["DELTAS"] >= datetime.timedelta(hours=delta_train_time)
            ].tolist()
            splits.insert(0, 0)
            splits.append(len(t.index))
            paths = [t.iloc[splits[n] : splits[n + 1]] for n in range(len(splits) - 1)]
            for path in paths:
                for b_from, b_to, delta in zip(
                    path["BERTHS"], path["BERTHS"][1:], path["DELTAS"][1:]
                ):
                    # Add the from berth to the graph
                    if berths[b_from]["FIXED"]:
                        self.graph.add_node(
                            b_from,
                            lon=berths[b_from]["LONGITUDE"] * 100000,
                            lat=berths[b_from]["LATITUDE"] * 100000,
                            fixed=True,
                        )
                    else:
                        self.graph.add_node(b_from, lon=None, lat=None, fixed=False)

                    # Add the to berth to the graph
                    if berths[b_to]["FIXED"]:
                        self.graph.add_node(
                            b_to,
                            lon=berths[b_to]["LONGITUDE"] * 100000,
                            lat=berths[b_to]["LATITUDE"] * 100000,
                            fixed=True,
                        )
                    else:
                        self.graph.add_node(b_to, lon=None, lat=None, fixed=False)

                    # Add the edge linking the berths to the graph
                    # Could use the delta in the future to weight edge
                    self.graph.add_edge(b_from, b_to, weight=1.0)

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

        return node_positions

    @timer
    def update_berths(self):
        """Update the berth positions in the database."""
        for node, data in self.graph.nodes(data=True):
            update = {
                "$set": {
                    "LONGITUDE": data["lon"],
                    "LATITUDE": data["lat"],
                    "SELECTED": True,
                    "EDGES": [[edge[1] for edge in list(self.graph.edges(node))]],
                }
            }
            self.mongo.update("BERTHS", {"NAME": node}, update)
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
    mongo = Mongo.connect(log, Config.MONGO_URI)

    if mongo is None:
        raise ConnectionError

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
