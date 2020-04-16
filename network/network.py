# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

import matplotlib.pyplot as plt 
from pymongo import MongoClient
import networkx as nx


log = logging.getLogger(__name__)

mongo_url = 'mongodb://{}:{}@mongo:27017'.format(
    os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    os.getenv('MONGO_INITDB_ROOT_PASSWORD'))
mongo_url_local = 'mongodb://{}:{}@localhost:27017'.format(
    os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    os.getenv('MONGO_INITDB_ROOT_PASSWORD'))


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser(description='collector')
    parser.add_argument('--verbose', action='store_true',
                        help='print debug level messages')
    return parser.parse_args()


def setup_logging(verbose):
    """Setup logging and stdout printing"""
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    if verbose:
        log.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


def main():
    """Main function called when collector starts."""
    args = parse_args()
    setup_logging(args.verbose)

    try:
        client = MongoClient(mongo_url_local)
        mongo = client.thetrains_mongo_test
        log.info("Connected to mongo at {}".format(mongo_url_local))
    except Exception:
        log.warning("Mongo connection error for {}, continue".format(
            mongo_url_local))

    G = nx.Graph()
    for movement in mongo.tm.find():
        G.add_edge(movement["from"], movement["to"])

    nx.draw_spring(G, with_labels=True, font_weight='bold')
    plt.show()


if __name__ == '__main__':
    main()
