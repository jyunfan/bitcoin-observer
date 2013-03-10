#!/usr/bin/env python
# synchroze local mongodb and trades on bitcoin-24

import datetime
import json
import logging
import urllib, urllib2
import time

import pymongo

DB = 'test'

def get_max_tradeid():
    connection = pymongo.MongoClient()
    db = connection[DB]
    rec = list(db.btc24.find().sort('_id',-1).limit(1))
    if rec:
        id = rec[0]['_id']
        logging.debug('maximum trade id is %d' % id)
        return id
    else:
        logging.debug('db is empty')
        return 0

def fetch_btc_trades(sinceid):
    # bitcoin-24 api:
    # https://bitcoin-24.com/api/EUR/trades.json?since=<id>
    # The return trades starts from sinceid+1
    #params = urllib.urlencode({'since': sinceid})
    req = 'https://bitcoin-24.com/api/EUR/trades.json?since=%d' % sinceid
    try:
        response = urllib2.urlopen(req).read()
    except:
        return []

    trades = json.loads(response)
    trades = [normalize_trade(trade) for trade in trades]
    return trades

def normalize_trade(trade):
    return {'_id': int(trade['tid']),
            'time': datetime.datetime.utcfromtimestamp(int(trade['date'])),
            'price': float(trade['price']),
            'amount': float(trade['amount'])
           }

def add_trades(trades):
    if not trades:
        return

    connection = pymongo.MongoClient()
    db = connection[DB]
    db.btc24.insert(trades)
    logging.debug('add %s trades' % len(trades))

def sync_btc24():
    maxid = get_max_tradeid()
    trades = fetch_btc_trades(maxid)
    add_trades(trades)

if __name__ == '__main__':
    logformat = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename='sync_btc24.log',
                        level=logging.DEBUG,
                        format=logformat)
    logger = logging.getLogger( __name__ )

    while True:
        sync_btc24()
        # update every 10 minutes
        time.sleep(600)
