# -*- coding: utf-8 -*-

import os
import sys
import signal
from time import sleep
from datetime import datetime
import json

import stomp  


class Collector(object):
    def __init__(self, conn):
        self.conn = conn
        self.counter = 0

    def connect_and_subscribe(self):
        # We use an exponential backoff and a max number of retry limit
        print("Attempting connection...")
        if self.counter >= 10:
            print('Maximum number of connection attempts made!')
            sys.exit(0)
        for wait in range(self.counter):
            sleep(pow(wait, 2))

        self.counter += 1
        self.conn.connect(
            username=os.environ["NETWORK_RAIL_USER"],
            passcode=os.environ["NETWORK_RAIL_PASS"],
            wait=True,
            headers={'client-id': os.environ["NETWORK_RAIL_USER"]}
        )
        self.conn.subscribe(
            '/topic/RTPPM_ALL',
            'thetrains-rtppm',
            ack='client-individual',
            headers={'activemq.subscriptionName': 'thetrains-rtppm'}
        )
        self.counter = 0  # Reset counter to zero
        print("connected!")

    def on_message(self, headers, message):
        self.conn.ack(
            id=headers['message-id'],
            subscription=headers['subscription']
        )
        print('Message: {}, Subscription: {}'.format(
            headers['message-id'], headers['subscription']))

        # Parse the message JSON and extract the required fields
        parsed = json.loads(message)
        timestamp = parsed['RTPPMDataMsgV1']['timestamp']
        parsed = parsed['RTPPMDataMsgV1']['RTPPMData']['NationalPage']
        total = parsed['NationalPPM']['Total']
        on_time = parsed['NationalPPM']['OnTime']
        late = parsed['NationalPPM']['Late']
        ppm = parsed['NationalPPM']['PPM']['text']
        rolling_ppm = parsed['NationalPPM']['RollingPPM']['text']

        date = datetime.fromtimestamp(int(timestamp)/1000.0)
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        print('{}: ({},{},{}), ({},{})'.format(
            date, total, on_time, late, ppm, rolling_ppm
        ))

    def on_error(self, headers, message):
        print('received an error "{}"'.format(message))
        self.connect_and_subscribe(self.conn)

    def on_disconnected(self):
        print('disconnected')
        self.connect_and_subscribe(self.conn)

    def exit_handler(self, sig, frame):
        print('Disconnecting...')
        self.conn.disconnect()
        sys.exit(0)


def main():
    # TODO: Use the heartbeat protocol
    conn = stomp.Connection(
        host_and_ports=[('datafeeds.networkrail.co.uk', 61618)],
        keepalive=True,
        vhost='datafeeds.networkrail.co.uk'
    )

    collector = Collector(conn)
    conn.set_listener('', collector)
    signal.signal(signal.SIGINT, collector.exit_handler)
    signal.signal(signal.SIGTERM, collector.exit_handler)
    collector.connect_and_subscribe()

    while 1:
        sleep(1)


if __name__ == '__main__':
    main()
