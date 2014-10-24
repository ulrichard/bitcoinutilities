#! /usr/bin/python
# Find the current balances for known addresses

import httplib2
import json
import locale, datetime, string, StringIO, csv
import dateutil.parser


class bitcoincharts:
    def __init__(self, symb):
        self.baseurl = 'http://api.bitcoincharts.com/v1/markets.json'
        h = httplib2.Http(".cache")
        h.debuglevel = 2
        resp, content = h.request(self.baseurl, "GET")
        jj = json.loads(content)
        for i in range(len(jj)):
            market = jj[i]
            if market['symbol'] == symb:
                self.market = market

    def last_close(self):
        price = float(self.market['close'])
        return price

    def ask(self):
        price = float(self.market['ask'])
        return price

    def bid(self):
        price = float(self.market['bid'])
        return price

