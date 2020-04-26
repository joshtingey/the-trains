# -*- coding: utf-8 -*-

"""
This module collects data from the national rail STOMP feeds. The
STOMPCollector class acts as the main connection handler while Feed
classes deal with handling individual messages.
"""

import sys
import signal
import time
import datetime
import logging
import asyncio
import enum

from decouple import config
import stomp
import orjson

from common.config import config_dict
from common.mongo import Mongo


log = logging.getLogger("collector")


class Feeds(enum.Enum):
    """
    Enumeration detailing the feed implementations.
    """
    PPM = 0
    TD = 1


class StompFeed(object):
    """
    Base feed handling class, which all others derive from.
    """

    def __init__(self, name, topic, durable, mongo):
        """
        Initialise the StompFeed.

        Args:
            name (int): 'Feeds' enumeration number
            topic (str): NR topic string
            durable (str): Durable connection name
            mongo (common.mongo.Mongo): Database class
        """
        self.name = name
        self.topic = topic
        self.durable = durable
        self.mongo = mongo

    async def handle_message(self, message):
        """
        Handle the JSON message, overide in dervied classes
        """
        raise NotImplementedError


class PPMFeed(StompFeed):
    """
    PPM feed handling class.
    """

    def __init__(self, mongo):
        """
        Initialise the PPMFeed.

        Args:
            mongo (common.mongo.Mongo): Database class
        """
        super().__init__(
            Feeds.PPM,
            "/topic/RTPPM_ALL",
            "thetrains-ppm",
            mongo
        )

    async def handle_message(self, message):
        """
        Handle the PPM JSON message.
        """
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return

        nat = parsed['RTPPMDataMsgV1']['RTPPMData']['NationalPage']
        doc = {
            "date": datetime.datetime.fromtimestamp(
                int(parsed['RTPPMDataMsgV1']['timestamp'])/1000),
            "total": int(nat['NationalPPM']['Total']),
            "on_time": int(nat['NationalPPM']['OnTime']),
            "late": int(nat['NationalPPM']['Late']),
            "ppm": float(nat['NationalPPM']['PPM']['text']),
            "rolling_ppm": float(nat['NationalPPM']['RollingPPM']['text'])
        }

        log.debug('{}: ({},{},{}), ({},{})'.format(
            doc["date"].strftime('%Y-%m-%d %H:%M:%S'),
            doc["total"],
            doc["on_time"],
            doc["late"],
            doc["ppm"],
            doc["rolling_ppm"]
        ))

        if self.mongo is not None:
            self.mongo.add("ppm", doc)


class TDFeed(StompFeed):
    """
    TD feed handling class.
    """

    def __init__(self, mongo):
        """
        Initialise the TDFeed.

        Args:
            mongo (common.mongo.Mongo): Database class
        """
        super().__init__(
            Feeds.TD,
            "/topic/TD_LNW_C_SIG_AREA",
            "thetrains-c-td",
            mongo
        )

    async def handle_message(self, message):
        """
        Handle the TD JSON message.
        """
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return

        for msg in parsed:
            if "CA_MSG" in msg.keys():
                step = msg["CA_MSG"]
                if step["area_id"] == "MP":
                    doc = {
                        "date": datetime.datetime.fromtimestamp(
                            int(step["time"])/1000),
                        "from": str(step["area_id"] + step["from"]),
                        "to": str(step["area_id"] + step["to"])
                    }

                    log.debug("time: {}, from: {}, to: {}".format(
                        doc["date"].strftime('%Y-%m-%d %H:%M:%S'),
                        doc["from"],
                        doc["to"]
                    ))

                    if self.mongo is not None:
                        self.mongo.add("td", doc)


def get_feed(feed, mongo):
    """
    Get the feed handling class.

    Args:
        feed: 'Feeds' enumeration number
        mongo (common.mongo.Mongo): Database class
    Returns:
        StompFeed: Feed handler class
    """
    if feed is Feeds.PPM:
        return PPMFeed(mongo)
    elif feed is Feeds.TD:
        return TDFeed(mongo)
    else:
        log.warning("Don't recongnise feed name")
        return None


class STOMPCollector(object):
    """
    STOMP collector class handles the connection and topic subscription.
    """

    def __init__(self, mongo, config):
        """
        Initialise the STOMPCollector.

        Args:
            mongo (common.mongo.Mongo): Database class
            config (common.config.Config): Configuration class
        """
        self.mongo = mongo  # Mongo database
        self.conn = None  # STOMP connection
        self.feeds = {}  # STOMP feed subscriptions
        self.attempts = config.CONN_ATTEMPTS  # Max number of conn attempts
        self.nr_user = config.NR_USER  # Network rail username
        self.nr_pass = config.NR_PASS  # Network rail password
        self.init()

    def init(self):
        """
        Initialise the stomp connection and signal handlers.
        """
        try:  # Setup the STOMP connection to network rail feed
            self.conn = stomp.Connection(
                host_and_ports=[('datafeeds.networkrail.co.uk', 61618)],
                keepalive=True,
                vhost='datafeeds.networkrail.co.uk',
                heartbeats=(100000, 100000)
            )
            self.conn.set_listener('handler', self)  # Register self
        except Exception as e:
            log.warning("STOMP setup error ({}), continue anyway".format(e))
            self.conn = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.exit_handler)
        signal.signal(signal.SIGTERM, self.exit_handler)

    def connect_and_subscribe(self):
        """
        Connect and resubscribe to all current feeds.
        """
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
        """
        Connect to the Network Rail STOMP Server.
        """
        for attempt in range(self.attempts):
            log.info("STOMP connection attempt: {}".format(attempt+1))
            time.sleep(pow(attempt, 2))  # Exponential backoff in wait

            try:  # Attempt STOMP connection to Network Rail
                log.info("Using {}:{}".format(self.nr_user, self.nr_pass))
                if self.conn is not None:
                    self.conn.connect(
                        username=self.nr_user,
                        passcode=self.nr_pass,
                        wait=True, headers={'client-id': self.nr_user}
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
        """
        Subscribe to a Network Rail STOMP feed.

        Args:
            name (int): 'Feeds' enumeration number
        """
        feed = get_feed(name, self.mongo)

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
                self.feeds[name] = feed
                log.info("Subscribed to feed ({})".format(name))
            except Exception as e:
                log.error("STOMP subscription error ({})".format(e))

    def unsubscribe(self, name):
        """
        Unsubscribe from a Network Rail STOMP feed.
        """
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
        """
        STOMP on_message handler.
        """
        log.debug('Got message')
        self.conn.ack(id=headers['message-id'],
                      subscription=headers['subscription'])

        for name, feed in self.feeds.items():
            if str(feed.topic) == str(headers["destination"]):
                asyncio.run(feed.handle_message(message))
                return

    def exit_handler(self, sig, frame):
        """
        Signal exit handler to close connections and exit.
        """
        log.info("Exit signal handler invoked({})".format(sig))
        for feed in self.feeds.keys():
            self.conn.unsubscribe(self.feeds[feed].durable)
            log.info("Unsubscribed from feed ({})".format(feed))
        self.conn.disconnect()
        log.info("Disconnected from NR STOMP Server")
        sys.exit(0)

    def on_error(self, headers, message):
        """
        STOMP on_error handler.
        """
        log.error('STOMP connection error "{}"'.format(message))
        self.connect_and_subscribe()

    def on_disconnected(self):
        """
        STOMP on_disconnected handler.
        """
        log.error('STOMP connection disconnect')
        self.connect_and_subscribe()

    def on_heartbeat_timeout(self):
        """
        STOMP on_heartbeat_timeout handler.
        """
        log.error('STOMP connection heartbeat timeout')
        self.connect_and_subscribe()


def main():
    """
    Main function called when collector starts.
    """
    conf = config_dict[config("ENV", cast=str, default="local")]
    conf.init_logging(log)

    mongo = Mongo(log, conf.MG_URI)

    collector = STOMPCollector(mongo, conf)
    collector.connect()

    if conf.PPM_FEED:
        collector.subscribe(Feeds.PPM)

    if conf.TD_FEED:
        collector.subscribe(Feeds.TD)

    while(1):
        time.sleep(1)


if __name__ == '__main__':
    main()
