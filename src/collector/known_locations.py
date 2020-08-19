# -*- coding: utf-8 -*-

"""This module generates the static berth location data from file."""

import json
import requests


def generate(mongo, log):
    """Generate the static berth locations and fill the database.

    Args:
        mongo (common.mongo.Mongo): database class
        log (logging.logger): logger to use
    """
    tiploc_file = open("./data/tiploc.json")
    tiploc_data = json.load(tiploc_file)
    tiploc_file.close()

    corpus_file = open("./data/corpus.json")
    corpus_data = json.load(corpus_file)["TIPLOCDATA"]
    corpus_file.close()

    smart_file = open("./data/smart.json")
    smart_data = json.load(smart_file)["BERTHDATA"]
    smart_file.close()

    log.info("Generating {} known berths...".format(len(tiploc_data)))
    for i, loc in enumerate(tiploc_data):  # We loop through all known locations
        if (i % 1000) == 0:
            log.info("Generated {} known berths...".format(i))
        r = requests.get(
            "https://api.getthedata.com/bng2latlong/"
            + str(loc["EASTING"])
            + "/"
            + str(loc["NORTHING"])
        )
        lon = float(r.json()["longitude"])
        lat = float(r.json()["latitude"])
        corpus = list(filter(lambda x: x["TIPLOC"] == loc["TIPLOC"], corpus_data))
        for corp in corpus:
            smart = list(filter(lambda x: x["STANOX"] == corp["STANOX"], smart_data))
            for s in smart:
                if s["STEPTYPE"] == "B":
                    key = None
                    set_data = {
                        "TD": str(s["TD"]),  # Train describer area for the berth
                        "TIPLOC": str(loc["TIPLOC"]),  # TIPLOC code for the berth
                        "STANOX": str(corp["STANOX"]),  # STANOX code for the berth
                        "STANME": str(s["STANME"]),  # STANME code for the berth
                        "DESCRIPTION": str(loc["NAME"]),  # Description of the berth
                        "OFFSET": str(s["BERTHOFFSET"]),  # event vs TRUST delta t
                        "PLATFORM": str(s["PLATFORM"]),  # Platform for this berth
                        "EVENT": str(s["EVENT"]),  # Event associated with this berth
                        "LONGITUDE": lon,  # Longitude of this berth
                        "LATITUDE": lat,  # Latitude of this berth
                        "FIXED": True,  # This is a fixed berth in position
                    }
                    # Add arrival or departure dependent info
                    if str(s["EVENT"]) in ["A", "C"]:
                        # A=Arrive Up, C=Arrive Down, therefore use TO berth
                        set_data["BERTH"] = str(s["TOBERTH"])
                        set_data["LINE"] = str(s["TOLINE"])
                        key = str(s["TD"]) + str(s["TOBERTH"])
                    elif str(s["EVENT"]) in ["B", "D"]:
                        # B=Depart Up, D=Depart Down, therefore use FROM berth
                        set_data["BERTH"] = str(s["FROMBERTH"])
                        set_data["LINE"] = str(s["FROMLINE"])
                        key = str(s["TD"]) + str(s["FROMBERTH"])
                    else:
                        continue

                    # Add to the database
                    mongo.client["BERTHS"].update_one(
                        {"NAME": key}, {"$set": set_data}, upsert=True
                    )
