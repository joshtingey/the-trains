# -*- coding: utf-8 -*-
import json

from tqdm import tqdm
import requests


def main():
    """
    Main function called when data script is run.
    """
    tiploc_d = None
    with open('../data/tiploc.json') as tiploc_json:
        tiploc_d = json.load(tiploc_json)

    corpus_d = None
    with open('../data/corpus.json') as corpus_json:
        corpus_d = json.load(corpus_json)['TIPLOCDATA']

    smart_d = None
    with open('../data/smart.json') as smart_json:
        smart_d = json.load(smart_json)['BERTHDATA']

    combined_data = {}
    for i, loc in enumerate(tqdm(tiploc_d)):
        r = requests.get('https://api.getthedata.com/bng2latlong/' +
                         str(loc['EASTING']) + '/' + str(loc['NORTHING']))
        lon = float(r.json()["longitude"])
        lat = float(r.json()["latitude"])
        corpus = list(filter(lambda x: x['TIPLOC'] == loc['TIPLOC'], corpus_d))
        for corp in corpus:
            smart = list(filter(lambda x: x['STANOX'] == corp['STANOX'], smart_d))
            for smar in smart:
                if smar['STEPTYPE'] == 'B':
                    comb_dict = {
                        'TIPLOC': str(loc['TIPLOC']),
                        'STANOX': str(corp['STANOX']),
                        'NAME': str(loc['NAME']),
                        'TD': str(smar['TD']),
                        'FROMBERTH': str(smar['FROMBERTH']),
                        'TOBERTH': str(smar['TOBERTH']),
                        'FROMLINE': str(smar['FROMLINE']),
                        'TOLINE': str(smar['TOLINE']),
                        'BERTHOFFSET': str(smar['BERTHOFFSET']),
                        'PLATFORM': str(smar['PLATFORM']),
                        'EVENT': str(smar['EVENT']),
                        'ROUTE': str(smar['ROUTE']),
                        'STANME': str(smar['STANME']),
                        'STEPTYPE': str(smar['STEPTYPE']),
                        'COMMENT': str(smar['COMMENT']),
                        'EASTING': int(loc['EASTING']),
                        'NORTHING': int(loc['NORTHING']),
                        'LON': lon,
                        'LAT': lat
                    }
                    combined_data[
                        str(smar['TD'])+str(smar['TOBERTH'])
                    ] = comb_dict

    with open('../data/locs.json', 'w') as outfile:
        json.dump(combined_data, outfile)


if __name__ == '__main__':
    main()
