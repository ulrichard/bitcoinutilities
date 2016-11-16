#! /usr/bin/python
# Find the current balances for known addresses by querying an electrum server
# Stratum protocol doc  : http://docs.electrum.org/en/latest/protocol.html
# jsonrpc documentation : https://pypi.python.org/pypi/jsonrpclib

import subprocess 
import json
from pycoin.tx.Tx import Tx

class electrum_cli:
    def balance(self, addr):
        p = subprocess.Popen(['electrum', 'getaddressbalance', addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = p.communicate()[0]

        try:
            data = json.loads(raw_data)
            balance = data['confirmed']
#            print(addr, balance)
            return balance
        except:
            return 0

    def history(self, addr):
        p = subprocess.Popen(['electrum', 'getaddresshistory', addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = p.communicate()[0]
        data = json.loads(raw_data)
        txs = []
        for tx in data:
            txs.append(tx['tx_hash'])
        return txs

    def load_tx(self, txid):
        p = subprocess.Popen(['electrum', 'gettransaction', txid], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = p.communicate()[0]

        data = json.loads(raw_data)
        txhex = data['hex']
        tx = Tx.from_hex(txhex)

        return tx
    

# test code
if __name__ == "__main__":
    cli = electrum_cli()
    bal = cli.balance('12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX')
    print(bal)

