# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import datetime
import logging
import asyncio
import argparse

from sqlalchemy import create_engine  
from sqlalchemy import Column, Integer, Float  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import stomp  
import orjson


log = logging.getLogger(__name__)


base = declarative_base()


# Define all database tables as python classes
class PPM(base):
    __tablename__ = 'ppm'

    date = Column(Integer, primary_key=True)
    total = Column(Integer)
    on_time = Column(Integer)
    late = Column(Integer)
    ppm = Column(Float)
    rolling_ppm = Column(Float)


class Collector(object):
    """Base collector class which all collector implementations derive from"""
    def __init__(self, db_url, attempts):
        self.init(db_url)
        self.max_attempts = attempts

    def init(self, db_url):
        """Initialise the DB connection, stomp connection and signal handlers"""
        log.info("Initialising collector with DB URL: {}".format(db_url))

        # Setup the database ORM session
        try:
            db = create_engine(db_url)
            Session = sessionmaker(db)
            self.session = Session()
            base.metadata.create_all(db)
        except Exception:
            log.warning("Can't connect to database, will continue anyway...")
            self.session = None

        # Setup the STOMP connection to network rail feed
        self.conn = stomp.Connection(
            host_and_ports=[('datafeeds.networkrail.co.uk', 61618)],
            keepalive=True,
            vhost='datafeeds.networkrail.co.uk',
            heartbeats=(100000, 100000)
        )
        self.conn.set_listener('', self)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.exit_handler)
        signal.signal(signal.SIGTERM, self.exit_handler)

    def connect_and_subscribe(self):
        """Connect and subscribe to the STOMP feed"""
        for attempt in range(self.max_attempts):
            log.info("STOMP connection attempt: {}".format(attempt+1))
            time.sleep(pow(attempt, 2))  # Exponential backoff in wait

            try:
                self.conn.connect(username=os.getenv("NR_USER"), passcode=os.getenv("NR_PASS"),
                    wait=True, headers={'client-id': os.getenv("NR_USER")})

                self.conn.subscribe(self.feed, self.durable_name, ack='client-individual',
                    headers={'activemq.subscriptionName': self.durable_name})
                
                log.info("STOMP connection successful")
                break  # Leave connection attempt loop and proceed
            except Exception as e:
                log.error("STOMP connection exception: {}".format(e))

            if attempt == (self.max_attempts-1):
                print('Maximum number of connection attempts made!')
                sys.exit(0)

    def on_message(self, headers, message):
        """STOMP on_message handler"""
        log.debug('Got message')
        self.conn.ack(id=headers['message-id'], subscription=headers['subscription'])
        asyncio.run(self.handle_message(message))

    async def handle_message(self, message):
        """Handle the JSON message"""
        raise NotImplementedError

    def exit_handler(self, sig, frame):
        """Signal exit handler to close connections and exit"""
        log.info("Exit signal handler invoked({}), disconnecting and exiting...".format(sig))
        self.conn.disconnect()
        if self.session is not None:
            self.session.close()
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


class RTPPMCollector(Collector):
    """Real-Time Public Performance Measure Collector"""
    def __init__(self, db_url, attempts):
        super().__init__(db_url, attempts)
        self.feed = '/topic/RTPPM_ALL'
        self.durable_name = 'thetrains-rtppm'

    async def handle_message(self, message):
        """Handle the RTPPM JSON message"""
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

        ppm_record = PPM(
            date=timestamp,
            total=total,
            on_time=on_time,
            late=late,
            ppm=ppm,
            rolling_ppm=rolling_ppm)

        if self.session is not None:
            self.session.add(ppm_record)
            self.session.commit()


class TMCollector(Collector):
    """Train Movements Collector"""
    def __init__(self, db_url, attempts):
        super().__init__(db_url, attempts)
        self.feed = '/topic/TRAIN_MVT_ED_TOC'
        self.durable_name = 'thetrains-tm'

    async def handle_message(self, message):
        """Handle the TM JSON message"""
        try:
            parsed = orjson.loads(message)
        except orjson.JSONDecodeError:
            log.error("Can't decode STOMP message")
            return


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser(description='collector')
    parser.add_argument('-t', '--type', help='collector type')
    parser.add_argument('-a', '--attempts', help='max number of connection attempts',
                        default=10)
    parser.add_argument('--verbose', action='store_true', help='print debug level messages')
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


def choose_collector(type, db_url, attempts):
    """Choose the derived collector class given the command line 'type' argument"""
    if type == 'RTPPM':
        return RTPPMCollector(db_url, attempts)
    elif type == 'TM':
        return TMCollector(db_url, attempts)
    else:
        log.error("Need to choose a correct collector type")
        exit(0)


def main():
    """Main function called when collector starts."""
    args = parse_args()
    db_url = 'postgresql://{}:{}@postgres:5432/{}'.format(
        os.getenv('DB_USER'), os.getenv('DB_PASS'), os.getenv('DB_NAME'))

    setup_logging(args.verbose)

    collector = choose_collector(args.type, db_url, args.attempts)
    collector.connect_and_subscribe()

    while(1):
        time.sleep(1)


if __name__ == '__main__':
    main()
