#! /usr/bin/python
# analyze a bitsquare transaction, starting from the taker fee transaction

import electrum_client
import locale, datetime, string, os, subprocess, json
import pycoin
import graphviz as gv
from pycoin.tx.TxOut import standard_tx_out_script
from pycoin.tx.script.tools import disassemble


#class 

class bitsquare:
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')

        homedir = os.environ['HOME']
        dirs = [homedir + '/Dokumente/BitCoin', homedir + '/.bitcoin', '.']
        for d in dirs:
            if os.path.isfile(d + '/bitsquare.json'):
                self.addresses = json.load(open(d + '/bitsquare.json'))
                break

        self.fee_addresses = self.addresses[0].items()[0][1]
        self.xpub = self.addresses[1].items()[0][1]
        self.participant_addresses = self.addresses[2].items()[0][1]
        self.ledger = electrum_client.electrum_cli()

        self.graph_detail = gv.Digraph(format='svg')
        self.graph_detail.node('bitsquare fees', color='red', shape='hexagon')
        self.handled_addresses = []
        self.handled_transactions = []

    def is_fee_addr(self, addr):
        if addr in self.fee_addresses:
            return True
        return False

    def is_lock_addr(self, addr):
        script = standard_tx_out_script(addr)
        script = disassemble(script)
        print(script)

    def is_taker_fee_tx(self, tx_hash):
        tx = self.ledger.load_tx(tx_hash)
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if self.is_fee_addr(addr):
                return True
        return False

    def get_addr_owner(self, addr):
        for user in self.participant_addresses:
            if addr in user[1]:
                return user[0]
        return ''
    
    def process_known_people(self):
        for user in self.participant_addresses:
            print(user)
        

    def handle_address(self, addr):
        if addr in self.handled_addresses:
            return
        # add to graph
        self.graph_detail.node(addr)
        if self.is_fee_addr(addr):
            self.graph_detail.edge(addr, 'bitsquare fees')
        elif self.is_lock_addr(addr):
            addr_txt = 'intermediate ' + addr
        # mark as handled
        self.handled_addresses.append(addr)
        # explore further
        history = self.ledger.history(addr)
#        for tx in history:
#            self.handle_tx(tx)

    def handle_tx(self, txid):
        if txid in self.handled_transactions:
            return

        tx = self.ledger.load_tx(txid)
        if self.is_taker_fee_tx(txid):
            tx_name = 'taker_fee ' + txid 
        else:
            tx_name = txid
        self.graph_detail.node(tx_name, shape='rectangle')

        for inp in tx.txs_in:
            addr = inp.bitcoin_address()
            self.handle_address(addr)
            previous_tx = self.ledger.load_tx(pycoin.serialize.b2h_rev(inp.previous_hash))
            prev_outp = previous_tx.txs_out[inp.previous_index]
            previous_coin_value = pycoin.convention.satoshi_to_btc(prev_outp.coin_value)
            self.graph_detail.edge(addr, tx_name, label=('%f' % previous_coin_value))
            
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            self.handle_address(addr)
            coin_value = pycoin.convention.satoshi_to_btc(outp.coin_value)
            self.graph_detail.edge(tx_name, addr, label=('%f' % coin_value))
        
    def write_graph(self, filename):
        self.graph_detail.render(filename=filename)
	
# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    bs = bitsquare()

    bs.handle_tx("f73b9555ce5c06b05653e35d148e9ebd5abc348736b9b64c811183abdea2c6a1")

    bs.process_known_people()

    filename = "/tmp/bitsquare_analysis"
    bs.write_graph(filename)

    subprocess.call(["eog", filename + '.svg'])
    


