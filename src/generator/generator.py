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

    def __init__(
        self,
        log,
        mongo,
        k,
        iter,
        cut_d,
        scale,
        delta_b,
        delta_t,
    ):
        """Initialise GraphGenerator.

        Args:
            log (logging.logger): Logger to use
            mongo (common.mongo.Mongo): Database class
            k (float): Spring layout k coefficient
            iter (int): Spring layout iterations
            cut_d (float): Cut distance for cutting long distance connections
            scale (int): Coordinate scaling for spring layout optimisation
            delta_b (int): Berths within delta seconds will be classed as the same
            delta_t (int): Split train data when there is a gap of delta hours
        """
        self.log = log
        self.mongo = mongo
        self.k = k
        self.iter = iter
        self.cut_d = cut_d
        self.scale = scale
        self.delta_b = delta_b
        self.delta_t = delta_t
        self.clean_delta = 2
        self.log.info(
            "k: {}, iter: {}, cut_d:{}, scale: {}, delta_b: {}, delta_t: {}".format(
                k, iter, cut_d, scale, delta_b, delta_t
            )
        )

    def run(self):
        """Build, tidy, and layout the graph."""
        self.log.info("Starting graph generation at {}".format(time.ctime()))
        try:
            # 1) Clean berths to remove stale train records
            self.clean_berths()

            # 2) Get all the berths, non are isolated as they are all connected
            self.get_berths()

            # 3) Get the single largest connected network
            self.get_largest_network()

            # 4) Run the first layout iteration
            self.run_layout(all_nodes=False)

            # 5) Remove long edges, isolated nodes and get largest network
            self.remove_distant_nodes(only_fixed=False)
            self.remove_isolated_nodes()
            self.get_largest_network()

            # 6) Run the second layout iteration
            self.run_layout(all_nodes=True)

            # 7) Remove long edges, isolated nodes and get largest network
            self.cut_d = 0.15
            self.remove_distant_nodes(only_fixed=False)
            self.remove_isolated_nodes()
            self.get_largest_network()

            # 8) Run the third layout iteration
            self.run_layout(all_nodes=True)

            # 9) Update the berth layout in the database
            self.update_berths()
        except Exception as e:
            self.log.warning("Could not complete generation: {}".format(e))

        self.log.info("Graph generation completed at {}".format(time.ctime()))

    @timer
    def clean_berths(self):
        """Clean the database berths to remove stale train records."""
        # Get the BERTHS and TRAINS from the database
        berths = self.mongo.get("BERTHS")
        if berths is None:
            raise Exception("BERTH or TRAIN data is empty!")

        # Get the current time and delta
        time_now = datetime.datetime.now()
        time_delta = datetime.timedelta(hours=self.clean_delta)

        num_cleaned = 0
        for berth in berths:
            if "LATEST_TIME" in berth:
                if (time_now - berth["LATEST_TIME"]) > time_delta:
                    num_cleaned += 1
                    update = {
                        "$set": {
                            "LATEST_TRAIN": "0000",
                            "LATEST_TIME": berth["LATEST_TIME"],
                        }
                    }
                    self.mongo.update("BERTHS", {"NAME": berth["NAME"]}, update)

        self.log.info("Cleaned {} berths".format(num_cleaned))

    @timer
    def get_berths(self):
        """Generate the initial graph from the berths stored in the database."""
        # Get the BERTHS and TRAINS from the database
        berths = {berth["NAME"]: berth for berth in self.mongo.get("BERTHS")}
        trains = self.mongo.get("TRAINS")
        if berths is None or trains is None:
            raise Exception("BERTH or TRAIN data is empty!")

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
            t = t[t["DELTAS"] >= datetime.timedelta(seconds=self.delta_b)]
            t = t.reset_index()

            # Remove duplicates of berths next to each other if exist
            t = t.loc[t["BERTHS"].shift(-1) != t["BERTHS"]]

            # Split the full train dataframe when there are large differences in time
            splits = t.index[
                t["DELTAS"] >= datetime.timedelta(hours=self.delta_t)
            ].tolist()
            splits.insert(0, 0)
            splits.append(len(t.index))
            paths = [
                t.iloc[splits[n] : splits[n + 1]]  # noqa: E203
                for n in range(len(splits) - 1)
            ]
            for path in paths:
                for b_from, b_to, delta in zip(
                    path["BERTHS"], path["BERTHS"][1:], path["DELTAS"][1:]
                ):
                    # Add the from berth to the graph
                    if berths[b_from]["FIXED"]:
                        self.graph.add_node(
                            b_from,
                            lon=berths[b_from]["LONGITUDE"],
                            lat=berths[b_from]["LATITUDE"],
                            fixed=True,
                        )
                    else:
                        self.graph.add_node(b_from, lon=None, lat=None, fixed=False)

                    # Add the to berth to the graph
                    if berths[b_to]["FIXED"]:
                        self.graph.add_node(
                            b_to,
                            lon=berths[b_to]["LONGITUDE"],
                            lat=berths[b_to]["LATITUDE"],
                            fixed=True,
                        )
                    else:
                        self.graph.add_node(b_to, lon=None, lat=None, fixed=False)

                    # Add the edge linking the berths to the graph
                    # Could use the delta in the future to weight edge
                    self.graph.add_edge(b_from, b_to, weight=1.0)

        self.log.info("Nodes from db {}".format(len(self.graph.nodes)))

    @timer
    def remove_isolated_nodes(self):
        """Remove isolated nodes from the graph."""
        self.graph.remove_nodes_from(list(nx.isolates(self.graph)))
        self.log.info(
            "Nodes remaining after 'remove_isolated_nodes': {}".format(
                len(self.graph.nodes)
            )
        )

    @timer
    def get_largest_network(self):
        """Just consider the single largest connected network."""
        largest_component = max(nx.connected_components(self.graph), key=len)
        self.graph = nx.Graph(self.graph.subgraph(largest_component))

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
        self.log.info(
            "Nodes remaining after 'remove_duplicate_locations': {}".format(
                len(self.graph.nodes)
            )
        )

    @timer
    def remove_distant_nodes(self, only_fixed=True):
        """Remove linked nodes that are distant from one another."""
        for edge in self.graph.edges:
            node_0 = self.graph.nodes[edge[0]]
            node_1 = self.graph.nodes[edge[1]]
            if node_0["lon"] is None or node_1["lon"] is None:
                continue
            d = math.sqrt(
                math.pow(node_0["lat"] - node_1["lat"], 2)
                + math.pow(node_0["lon"] - node_1["lon"], 2)
            )
            if only_fixed and node_0["fixed"] and node_1["fixed"] and d >= self.cut_d:
                self.graph.remove_edge(edge[0], edge[1])
            elif not only_fixed and d >= self.cut_d:
                self.graph.remove_edge(edge[0], edge[1])
        self.log.info(
            "Nodes remaining after 'remove_distant_nodes': {}".format(
                len(self.graph.nodes)
            )
        )

    @timer
    def remove_floating_nodes(self):
        """Remove nodes that do not lie between fixed nodes."""
        known = [n for n, d in self.graph.nodes().items() if d["fixed"] is True]
        c_score = nx.algorithms.betweenness_centrality_subset(self.graph, known, known)
        nodes_between = [x for x in c_score if c_score[x] != 0.0]
        nodes_between.extend(known)  # Add on fixed nodes
        self.graph = self.graph.subgraph(nodes_between)
        self.log.info(
            "Nodes remaining after 'remove_floating_nodes': {}".format(
                len(self.graph.nodes)
            )
        )

    @timer
    def run_layout(self, all_nodes=False):
        """Run the spring layout that positions all the nodes."""
        # Run the spring layout algorithm on the network
        fixed_positions = dict(
            (n, [d["lat"] * self.scale, d["lon"] * self.scale])
            for n, d in self.graph.nodes().items()
            if d["fixed"] is True
        )
        if all_nodes:
            all_positions = dict(
                (n, [d["lat"] * self.scale, d["lon"] * self.scale])
                for n, d in self.graph.nodes().items()
            )

        self.log.info("There are {} fixed nodes".format(len(fixed_positions)))

        if all_nodes:
            node_positions = nx.spring_layout(
                self.graph,
                k=self.k,
                pos=all_positions,
                fixed=fixed_positions.keys(),
                iterations=self.iter,
            )
        else:
            node_positions = nx.spring_layout(
                self.graph,
                k=self.k,
                pos=fixed_positions,
                fixed=fixed_positions.keys(),
                iterations=self.iter,
            )

        for node, position in node_positions.items():
            self.graph.nodes[node]["lat"] = position[0] / self.scale
            self.graph.nodes[node]["lon"] = position[1] / self.scale

        self.graph = nx.Graph(self.graph)  # Unfreeze graph
        return node_positions

    @timer
    def update_berths(self):
        """Update the berth positions in the database."""
        # First unselect all berths
        update = {"$set": {"SELECTED": False}}
        self.mongo.update("BERTHS", {}, update, many=True)

        # Now update the selected berths
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
        Config.GENERATOR_ITER,
        Config.GENERATOR_CUT_D,
        Config.GENERATOR_SCALE,
        Config.GENERATOR_DELTA_B,
        Config.GENERATOR_DELTA_T,
    )

    # Run the graph generator in a loop, run every GRAPH_UPDATE_RATE seconds
    while 1:
        gen.run()
        time.sleep(Config.GENERATOR_RATE)


if __name__ == "__main__":
    main()
