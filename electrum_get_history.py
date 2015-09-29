#!/usr/bin/env python

import sys, imp, os
try:
    import electrum
except:
    sys.path.append(os.environ['HOME'] + '/sourcecode/electrum')
    imp.load_module('electrum', *imp.find_module('lib'))
    import electrum

script_dir = os.path.dirname(os.path.realpath(__file__))

class ElectrumClient:
    def __init__(self, server = None, proxy = None):
        options={}
#        options['electrum_path'] = os.environ['HOME'] + '/.electrum'
        options['electrum_path'] = script_dir
        self.conf = electrum.SimpleConfig(options)
        if None != server:
            self.conf.set_key('server', server, False)
        if None != proxy:
            self.conf.set_key('proxy', proxy, False)
        if None != server and None != proxy:
            self.conf.set_key('auto_cycle', False, False)
        else:
            self.conf.set_key('auto_cycle', True, False)
        print 'server: ', self.conf.get('server')
        print 'proxy:  ', self.conf.get('proxy')
#        self.sock = electrum.daemon.get_daemon(self.conf, True)
#        self.netw = electrum.NetworkProxy(self.sock, self.conf)
        self.netw = electrum.Network(self.conf)
        self.netw.start()
        self.timeout = 10000 # default is 10'000'000

    def get_history(self, addr):
        requ = [('blockchain.address.get_history', [addr])]
        hist = self.netw.synchronous_get(requ, self.timeout)[0]
        return hist

    def get_transaction_details(self, tx_hash):
        requ = [('blockchain.transaction.get', [tx_hash])]
        raw = self.netw.synchronous_get(requ, self.timeout)[0] 
        return electrum.Transaction.deserialize(raw)

    def get_balance(self, address):
        hist = self.get_history(address)
        if hist == ['*']: return 0
        bal = 0
        received_coins = []   # list of coins received at address

        for elem in hist:
            tx = self.get_transaction_details(elem['tx_hash'])
            if not tx: continue

            for i, (addr, value) in enumerate(tx.get_outputs()):
                if addr == address:
                    key = elem['tx_hash'] + ':%d'%i
                    received_coins.append(key)

        for elem in hist:
            tx = self.get_transaction_details(elem['tx_hash'])
            if not tx: continue

            for i, (addr, value) in enumerate(tx.get_outputs()):
                key = elem['tx_hash'] + ':%d'%i
                if addr == address:
                    bal += value

        return bal


# test code
if __name__ == "__main__":
    cli = ElectrumClient('ulrichard.ch:50002:s', '')
#    cli = ElectrumClient()
    addr = '1JuArrY4wpG9v6bgDbuugPPvbZTTn5Vxou'

    hist = cli.get_history(addr)
    print 'transaction history for: ', addr
    print 'transaction count: ', len(hist)
#    electrum.print_json(hist)
    
    for elem in hist:
        tx = cli.get_transaction_details(elem['tx_hash'])
        print 'inputs count: ', len(tx.inputs), ' outputs count: ', len(tx.outputs)

    print 'balance: ', cli.get_balance(addr) / 100000000.0



