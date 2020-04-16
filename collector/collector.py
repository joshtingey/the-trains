# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import logging
import asyncio
import argparse
import enum

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import stomp
import orjson


log = logging.getLogger(__name__)
base = declarative_base()


postgres_url = 'postgresql://{}:{}@postgres:5432/{}'.format(
    os.getenv('DB_USER'), os.getenv('DB_PASS'), os.getenv('DB_NAME'))
postgres_url_local = 'postgresql://{}:{}@localhost:5432/{}'.format(
    os.getenv('DB_USER'), os.getenv('DB_PASS'), os.getenv('DB_NAME'))
mongo_url = 'mongodb://{}:{}@mongo:27017'.format(
    os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    os.getenv('MONGO_INITDB_ROOT_PASSWORD'))
mongo_url_local = 'mongodb://{}:{}@localhost:27017'.format(
    os.getenv('MONGO_INITDB_ROOT_USERNAME'),
    os.getenv('MONGO_INITDB_ROOT_PASSWORD'))


class Feeds(enum.Enum):
    PPM = 0
    TM = 1
    TD = 2


class StompFeed():
    def __init__(self, name, topic, durable):
        self.name = name
        self.topic = topic
        self.durable = durable
        self.postgres = None

    def set_db(self, postgres, mongo):
        """Set the databases"""
        self.postgres = postgres
        self.mongo = mongo

    async def handle_message(self, message):
        """Handle the JSON message"""
        raise NotImplementedError


class PPMFeed(StompFeed):
    def __init__(self):
        super().__init__(
            Feeds.PPM,
            "/topic/RTPPM_ALL",
            "thetrains-ppm"
        )

    class ppm_table(base):
        """Define the PPM database table"""
        __tablename__ = 'ppm'
        date = Column(Integer, primary_key=True)
        total = Column(Integer)
        on_time = Column(Integer)
        late = Column(Integer)
        ppm = Column(Float)
        rolling_ppm = Column(Float)

    async def handle_message(self, message):
        """Handle the PPM JSON message"""
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return

        timestamp = int(parsed['RTPPMDataMsgV1']['timestamp']) / 1000
        parsed = parsed['RTPPMDataMsgV1']['RTPPMData']['NationalPage']
        total = int(parsed['NationalPPM']['Total'])
        on_time = int(parsed['NationalPPM']['OnTime'])
        late = int(parsed['NationalPPM']['Late'])
        ppm = float(parsed['NationalPPM']['PPM']['text'])
        rolling_ppm = float(parsed['NationalPPM']['RollingPPM']['text'])

        date = datetime.datetime.fromtimestamp(timestamp)
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        log.debug('{}: ({},{},{}), ({},{})'.format(
            date, total, on_time, late, ppm, rolling_ppm
        ))

        ppm_record = self.ppm_table(
            date=timestamp,
            total=total,
            on_time=on_time,
            late=late,
            ppm=ppm,
            rolling_ppm=rolling_ppm
        )

        if self.postgres is not None:
            self.postgres.add(ppm_record)
            self.postgres.commit()


class TMFeed(StompFeed):
    def __init__(self):
        super().__init__(
            Feeds.TM,
            "/topic/TRAIN_MVT_ED_TOC",
            "thetrains-ed-tm"
        )

    async def handle_message(self, message):
        """Handle the TM JSON message"""
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return

        log.debug("Length of TM message: {}".format(len(parsed)))
        for msg in parsed:
            if msg["header"]["msg_type"] == "0003":
                log.debug("stanox: {}, type: {}, train: {}".format(
                    msg["body"]["reporting_stanox"],
                    msg["body"]["event_type"],
                    msg["body"]["train_id"]
                ))


class TDFeed(StompFeed):
    def __init__(self):
        super().__init__(
            Feeds.TD,
            "/topic/TD_LNW_C_SIG_AREA",
            "thetrains-c-td"
        )

    async def handle_message(self, message):
        """Handle the TM JSON message"""
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return

        for msg in parsed:
            if "CA_MSG" in msg.keys():
                step = msg["CA_MSG"]
                if step["area_id"] == "MP":
                    movement = {
                        "date": datetime.datetime.fromtimestamp(
                            int(step["time"])/1000),
                        "from": str(step["area_id"] + step["from"]),
                        "to": str(step["area_id"] + step["to"])
                    }

                    log.debug("time: {}, from: {}, to: {}".format(
                        movement["date"].strftime('%Y-%m-%d %H:%M:%S'),
                        movement["from"],
                        movement["to"]
                    ))

                    if self.mongo is not None:
                        try:
                            self.mongo.tm.insert_one(movement)
                        except Exception as e:
                            log.warning("DB error ({})".format(e))


def get_feed(feed):
    if feed is Feeds.PPM:
        return PPMFeed()
    elif feed is Feeds.TM:
        return TMFeed()
    elif feed is Feeds.TD:
        return TDFeed()
    else:
        log.warning("Don't recongnise feed name")
        return None


class STOMPCollector(object):
    """STOMP collector class handles the connection and topic subscription"""

    def __init__(self, attempts):
        self.postgres = None  # Postgres database session
        self.mongo = None  # Mongo database
        self.conn = None  # STOMP connection
        self.feeds = {}  # STOMP feed subscriptions
        self.attempts = attempts  # Max number of connection attempts
        self.init()

    def init_postgres(self, url):
        try:
            db = create_engine(url)
            Session = sessionmaker(db)
            self.postgres = Session()
            base.metadata.create_all(db)
            log.info("Connected to postgres at {}".format(url))
        except Exception:
            log.warning("Postgres connection error for {}, continue".format(
                url))
            self.postgres = None

    def init_mongo(self, url):
        try:
            client = MongoClient(url)
            self.mongo = client.thetrains_mongo_test
            log.info("Connected to mongo at {}".format(url))
        except Exception:
            log.warning("Mongo connection error for {}, continue".format(
                url))
            self.mongo = None

    def init(self):
        """Initialise the DB, stomp connection and signal handlers"""
        self.init_postgres(postgres_url_local)
        if self.postgres is None:
            self.init_postgres(postgres_url)

        self.init_mongo(mongo_url_local)
        if self.mongo is None:
            self.init_mongo(mongo_url)

        try:  # Setup the STOMP connection to network rail feed
            self.conn = stomp.Connection(
                host_and_ports=[('datafeeds.networkrail.co.uk', 61618)],
                keepalive=True,
                vhost='datafeeds.networkrail.co.uk',
                heartbeats=(100000, 100000)
            )
            self.conn.set_listener('handler', self)  # Register self
            # self.conn.set_listener('stats', stomp.StatsListener())
            # self.conn.set_listener('print', stomp.PrintingListener())
        except Exception as e:
            log.warning("STOMP setup error ({}), continue anyway".format(e))
            self.conn = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.exit_handler)
        signal.signal(signal.SIGTERM, self.exit_handler)

    def connect_and_subscribe(self):
        self.connect()
        for feed in self.feeds.keys():
            try:  # Attempt to subscribe to the feed
                self.conn.subscribe(
                    self.feeds[feed].topic,
                    self.feeds[feed].durable,
                    ack='client-individual',
                    headers={'activemq.subscriptionName':
                             self.feeds[feed].durable}
                )
                log.info("Subscribed to {}".format(self.feeds[feed].name))
            except Exception as e:
                log.error("STOMP subscription error ({})".format(e))

    def connect(self):
        """Connect to the Network Rail STOMP Server"""
        for attempt in range(self.attempts):
            log.info("STOMP connection attempt: {}".format(attempt+1))
            time.sleep(pow(attempt, 2))  # Exponential backoff in wait

            try:  # Attempt STOMP connection to Network Rail
                if self.conn is not None:
                    self.conn.connect(
                        username=os.getenv("NR_USER"),
                        passcode=os.getenv("NR_PASS"),
                        wait=True, headers={'client-id': os.getenv("NR_USER")}
                    )
                else:
                    log.warning("No STOMP connection to connect to")
                    break

                log.info("STOMP connection successful")
                break  # Leave connection attempt loop and proceed
            except Exception as e:
                log.error("STOMP connection error ({}), retry...".format(e))

            if attempt == (self.attempts-1):
                log.fatal("Maximum number of connection attempts made")
                sys.exit(0)

    def subscribe(self, name):
        """Subscribe to a Network Rail STOMP feed"""
        feed = get_feed(name)  # Get the correct feed implementation

        if name in self.feeds:  # Check if we already have this feed
            log.warning("Already subscribed to this feed")
            return

        if feed is not None:
            try:  # Attempt to subscribe to the feed
                self.conn.subscribe(
                    feed.topic,
                    feed.durable,
                    ack='client-individual',
                    headers={'activemq.subscriptionName': feed.durable}
                )
                feed.set_db(self.postgres, self.mongo)
                self.feeds[name] = feed
                log.info("Subscribed to feed ({})".format(name))
            except Exception as e:
                log.error("STOMP subscription error ({})".format(e))

    def unsubscribe(self, name):
        """Unsubscribe from a Network Rail STOMP feed"""
        if name in self.feeds:
            try:
                self.conn.unsubscribe(self.feeds[name].durable)
                del self.feeds[name]
                log.info("Unsubscribed from feed ({})".format(name))
            except Exception as e:
                log.error("STOMP unsubscribe error ({}), keep feed".format(e))
                return
        else:
            log.warning("No feed with that name")

    def on_message(self, headers, message):
        """STOMP on_message handler"""
        log.debug('Got message')
        self.conn.ack(id=headers['message-id'],
                      subscription=headers['subscription'])

        for name, feed in self.feeds.items():
            if str(feed.topic) == str(headers["destination"]):
                asyncio.run(feed.handle_message(message))
                return

    async def handle_message(self, message):
        """Handle the JSON message"""
        raise NotImplementedError

    def exit_handler(self, sig, frame):
        """Signal exit handler to close connections and exit"""
        log.info("Exit signal handler invoked({})".format(sig))
        for feed in self.feeds.keys():
            self.conn.unsubscribe(self.feeds[feed].durable)
            log.info("Unsubscribed from feed ({})".format(feed))
        self.conn.disconnect()
        log.info("Disconnected from NR STOMP Server")
        if self.postgres is not None:
            self.postgres.close()
            log.info("Closed DB session")
        sys.exit(0)

    def on_error(self, headers, message):
        """STOMP on_error handler"""
        log.error('STOMP connection error "{}"'.format(message))
        self.connect_and_subscribe()

    def on_disconnected(self):
        """STOMP on_disconnected handler"""
        log.error('STOMP connection disconnect')
        self.connect_and_subscribe()

    def on_heartbeat_timeout(self):
        """STOMP on_heartbeat_timeout handler"""
        log.error('STOMP connection heartbeat timeout')
        self.connect_and_subscribe()


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser(description='collector')
    parser.add_argument('-a', '--attempts', default=10,
                        help='max number of connection attempts')
    parser.add_argument('--verbose', action='store_true',
                        help='print debug level messages')
    parser.add_argument('--ppm', action='store_true',
                        help='subscribe to ppm feed')
    parser.add_argument('--tm', action='store_true',
                        help='subscribe to tm feed')
    parser.add_argument('--td', action='store_true',
                        help='subscribe to td feed')
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

    collector = STOMPCollector(args.attempts)
    collector.connect()

    if args.ppm:
        collector.subscribe(Feeds.PPM)

    if args.tm:
        collector.subscribe(Feeds.TM)

    if args.td:
        collector.subscribe(Feeds.TD)

    while(1):
        time.sleep(1)


if __name__ == '__main__':
    main()
