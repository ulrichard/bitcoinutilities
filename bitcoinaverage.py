#! /usr/bin/python
# Find the current balances for known addresses

import httplib2
import json
import locale, datetime, string, StringIO, csv
import dateutil.parser

class bitcoinaverage:
    def __init__(self, currency):
        self.currency = currency
        self.values = {}
        url = 'https://api.bitcoinaverage.com/history/%s/per_day_all_time_history.csv' % currency	
        h = httplib2.Http(".cache")
        h.debuglevel = 2
        resp, content = h.request(url, "GET")
        f = StringIO.StringIO(content)
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if len(row) > 4 and not row[0] == 'datetime':
                date = dateutil.parser.parse(row[0])
                avg  = float(row[3])
                if avg > 0:
                    self.values[date.date()] = avg
        print 'got average prices for ', currency, ' for ', len(self.values), ' days'

    def get_avg(self, day):
        if self.values.has_key(day):
            return self.values[day]
        return 0

