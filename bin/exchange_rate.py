#!/usr/bin/env python
# Provide exchange rates in a given time period
# Return JSON

# For converting python datetime object to JSON, see
# [1] http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python
# [2] http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript

# std lib
from datetime import datetime
import json
import time

# 3rd lib
from bottle import route, run, error, request, static_file
import pymongo
from bson import json_util

# db name in mongo
DB = 'test'

# Default
# Example /ex/btc24eur?start=
@route('/ex/btc24eur')
def btx24eur():
    # default timestamp for start is last 24 hours
    start = int(request.query.start) if request.query.start else int(time.time()-86400)
    # default timestamp for end is now
    end   = int(request.query.end) if request.query.end else int(time.time())

    connection = pymongo.MongoClient()
    db = connection[DB]

    trades = db.btc24.find({'time':{
        '$gte': datetime.utcfromtimestamp(start),
        '$lte': datetime.utcfromtimestamp(end)}})

    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
    return json.dumps(list(trades), default=dthandler)

@route('/')
def homepage():
    return static_file('exchange.html', root='static')

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

@error(404)
def error404(error):
    return 'Nothing here'

run(host='localhost', port=8080, debug=True)
