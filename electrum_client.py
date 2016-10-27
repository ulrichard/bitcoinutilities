#! /usr/bin/python
# Find the current balances for known addresses by querying an electrum server
# Stratum protocol doc  : http://docs.electrum.org/en/latest/protocol.html
# jsonrpc documentation : https://pypi.python.org/pypi/jsonrpclib

import subprocess 
import json

class electrum_cli:
    def __init__(self, addr):
        self.addr = addr

    def balance(self):
        p = subprocess.Popen(['electrum', 'getaddressbalance', self.addr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = p.communicate()[0]
    
        data = json.loads(raw_data)
        return data['confirmed']


# test code
if __name__ == "__main__":
    cli = electrum_cli('12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX')
    bal = cli.balance()
    print(bal)

