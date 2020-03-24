# -*- coding: utf-8 -*-

import os
import requests
import json


def main():
    try:  # Transport API test
        requestString = 'http://transportapi.com/v3/uk/train/station/MAN/live.json?app_id={}&app_key={}'.format(
            os.environ['TRANSPORTAPI_ID'], os.environ['TRANSPORTAPI_KEY'])
        r = requests.get(requestString)
        parsed = json.loads(r.text)
        for d in parsed["departures"]["all"]:
            print("Origin:{}, Destination:{}, Departure Time:{},".format(
                d["origin_name"],
                d["destination_name"],
                d["aimed_departure_time"]))
    except Exception:
        raise ConnectionError


if __name__ == '__main__':
    main()
