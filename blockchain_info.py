#! /usr/bin/python
# Find the current balances for known addresses

import httplib2
import json
import datetime, string

class blockchain:
    def __init__(self, addr, withTx):
        self.baseurl = 'https://blockchain.info/address'
        h = httplib2.Http(".cache")
        h.debuglevel = 2
        url = '%s/%s?format=json&limit=0' % (self.baseurl, addr)
        resp, content = h.request(url, "GET")
        self.jj = json.loads(content)

        if not withTx:
            return

        self.transactions = {}
        pagesize = 50
        offset = 0
        count = pagesize
        txcount = 0
        while offset < count :	
            print 'downloading with offset ', offset
            url = '%s/%s?format=json&limit=%d&offset=%d' % (self.baseurl, addr, pagesize, offset)
            offset += pagesize
            resp, content = h.request(url, "GET")
            self.jj = json.loads(content)
            count = int(self.jj['n_tx'])
            for tx in self.jj['txs']:
                timestamp = int(tx['time'])
                timestamp = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)
                if not self.transactions.has_key(timestamp.date()):
                    self.transactions[timestamp.date()] = 0
                for dest in tx['out']:
                    if dest.has_key('addr') and dest['addr'] == addr:
                        self.transactions[timestamp.date()] += int(dest['value'])
                        txcount += 1
        print 'total number of transactions: ', count 
        print 'number of receiving transactions: ', txcount 

    def total_received(self):
        ammount = float(self.jj['total_received']) / 100000000
        return ammount

    def balance(self):
        ammount = float(self.jj['final_balance']) / 100000000
        return ammount

    def tx_count(self):
        return int(self.jj['n_tx'])

    def get_transactions(self):
        return self.transactions


