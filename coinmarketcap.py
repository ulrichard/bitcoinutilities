#! /usr/bin/python
# Find the current price for cryptocurrencies

import httplib2
import json
import locale, datetime, string, StringIO, csv
import dateutil.parser


class coinmarketcap:
    def __init__(self, symb):
        self.url = 'https://api.coinmarketcap.com/v1/ticker/%s/' % symb
        h = httplib2.Http(".cache")
        h.debuglevel = 2
        resp, content = h.request(self.url, "GET")
        jj = json.loads(content)
        self.asset = jj[0]

    def price(self):
        return self.asset['price_usd']


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    print('BTC: %f' % coinmarketcap('bitcoin').price())
    print('ETH: %f' % coinmarketcap('ethereum').price())
    print('NMC: %f' % coinmarketcap('namecoin').price())
    print('LTC: %f' % coinmarketcap('litecoin').price())
    print('XDA: %f' % coinmarketcap('dash').price())
    print('XMN: %f' % coinmarketcap('monero').price())
