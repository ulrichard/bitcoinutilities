#! /usr/bin/python
# Find the current balances for known addresses by querying an electrum server
# Stratum protocol doc  : http://docs.electrum.org/en/latest/protocol.html
# jsonrpc documentation : https://pypi.python.org/pypi/jsonrpclib

import jsonrpclib 
import json

class electrum_cli:
    def __init__(self, addr, withTx):
        self.addr = addr
#        self.host = 'https://ulrichard.ch'
#        self.port = 50002
        host = 'https://192.168.2.8'
        port = 50001
        self.server = jsonrpclib.Server('http://%s:%d' % (host, port)) 

#    def total_received(self):
#        ammount = self.balance()
#        return ammount

    def balance(self):
        resp = self.server.blockchain.address.get_balance(self.addr)
        ammount = resp['confirmed'] / 100000000
        return ammount

#    def tx_count(self):
#        return 42

#    def get_transactions(self):
#        return self.transactions


