#! /usr/bin/python
# Find the current balances for known addresses

import httplib2
import json
import locale, datetime, string, StringIO, csv
import dateutil.parser
import pycoin.key.BIP32Node, pycoin.key.Key, pycoin.key.electrum


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

class accounts:
    def __init__(self, filename):
        locale.setlocale(locale.LC_ALL, '')
        self.addresses = json.load(open(filename))

    def balances(self, filterName = ''):
        balance = {}
        for i in range(len(self.addresses)):
            person = self.addresses[i]
            name = person.items()[0][0]
            if '' != filterName and name != filterName:
                continue
            balance[name] = {}
            for j in range(len(person.items()[0][1])):
                addr = person.items()[0][1][j].items()[0][1]
                desc = person.items()[0][1][j].items()[0][0]
                if len(addr) < 40:
                    # regular address
                    ledger = blockchain(addr, False)
                    bal  = ledger.balance()
                    balance[name][addr] = [bal, desc]
                elif 'xpub' == addr[0:4]:
                    # deterministic hierarchical public key
                    kk = pycoin.key.BIP32Node.BIP32Node.from_hwif(addr)
                    for j in range(2):
                        gap = 0
                        for i in range(99999):
                            keypath = "%d/%d.pub" % (j, i)
                            #print(keypath)
                            addr = kk.subkey_for_path(keypath).address()
                            #print i, j, addr
                            ledger = blockchain(addr, False)
                            bal  = ledger.balance()
                            balance[name][addr] = [bal, '%s_%s_%d' % (desc, 'P' if 0 == j else 'Chg', i)]
                            if bal == 0:
                                if 0 == ledger.tx_count():
                                    gap += 1
                                    if gap > 10:
                                        break
                else:
                    kk = pycoin.key.electrum.ElectrumWallet(addr)
                    for i in range(20):
                        for j in range(2):
                            keypath = "%d/%d" % (j, i)
                            addr = kk.subkey(keypath).address()
                            #print i, j, addr
                            ledger = blockchain(addr, False)
                            bal  = ledger.balance()
                            balance[name][addr] = [bal, '%s_%s_%d' % (desc, 'P' if 0 == j else 'Chg', i)]

        return balance

