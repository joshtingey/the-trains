# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging

from sqlalchemy import create_engine  
from sqlalchemy import Column, Integer, Float  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import networkx as nx


log = logging.getLogger(__name__)
base = declarative_base()


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

    db_url = 'postgresql://{}:{}@postgres:5432/{}'.format(
        os.getenv('DB_USER'), os.getenv('DB_PASS'), os.getenv('DB_NAME'))

    try:  # Setup the database ORM session
        db = create_engine(db_url)
        Session = sessionmaker(db)
        session = Session()
        base.metadata.create_all(db)
    except Exception:
        log.warning("DB connection error, will continue anyway")
        session = None

    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3)])
    log.info(list(G.edges))


if __name__ == '__main__':
    main()
