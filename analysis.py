#! /usr/bin/python
# analyze a bitsquare transaction, starting from the taker fee transaction

import electrum_client
import locale, datetime, string, os, subprocess, json
import pycoin
import graphviz as gv
from pycoin.tx.TxOut import standard_tx_out_script
from pycoin.tx.script.tools import disassemble


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
        for user in self.participant_addresses:
            self.graph_detail.node(user.items()[0][0], color='green', shape='hexagon')

        self.handled_addresses = set()
        self.handled_transactions = set()

    def is_fee_addr(self, addr):
        if addr in self.fee_addresses:
            return True
        return False

    def is_lock_addr(self, addr):
        try:
            script = standard_tx_out_script(addr)
            script = disassemble(script)
            print(script)
        except:
            print('error analyzing addr: ', addr)
        return False

    def is_offer_fee_tx(self, tx):
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if self.is_fee_addr(addr):
                if self.get_tx_out_sum(tx) >= 0.015:
                    return True
        return False

    def is_taker_fee_tx(self, tx):
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if self.is_fee_addr(addr):
                if self.get_tx_out_sum(tx) < 0.015:
                    return True
        return False

    def is_deposit_tx(self, tx):
        if len(tx.txs_in) != 2:
            return False
        if len(tx.txs_out) != 2:
            return False
        has_offer = False
        has_taker = False
        for inp in tx.txs_in:
            addr = inp.bitcoin_address()
            if addr == '(unknown)':
                return False
            previous_tx = self.ledger.load_tx(pycoin.serialize.b2h_rev(inp.previous_hash))
            if self.is_offer_fee_tx(previous_tx):
                has_offer = True
            elif self.is_taker_fee_tx(previous_tx):
                has_taker = True
        if not has_offer or not has_taker:
            return False
        has_p2sh = False
        has_opret = False
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if addr is None:
                has_opret = True
            elif addr[0] == '3':
                has_p2sh = True
        if not has_p2sh or not has_opret:
            return False
        return True

    def is_payout(self, tx):
        if len(tx.txs_in) != 1:
            return False
        if len(tx.txs_out) != 2:
            return False
        has_deposit = False
        for outp in tx.txs_out:
            coin_value = pycoin.convention.satoshi_to_btc(outp.coin_value)
            if coin_value == 0.01:
                has_deposit = True
        return has_deposit

    def get_tx_out_sum(self, tx):
        sumval = 0
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if not addr is None:
                coin_value = pycoin.convention.satoshi_to_btc(outp.coin_value)
                sumval = sumval + coin_value
        return sumval

    def get_addr_owner(self, addr):
        for user in self.participant_addresses:
            if addr in user.items()[0][1]:
                return user.items()[0][0]
        return ''
    
    def process_known_people(self):
        for user in self.participant_addresses:
            for addr in user.items()[0][1]:
                self.handle_address(addr)
        

    def handle_address(self, addr, depth = 3):
        if addr in self.handled_addresses or addr is None or addr == '(unknown)':
            return
        print('handle_address(', addr, ')')
        # add to graph
        try:
            self.graph_detail.node(addr)
        except:
            print('problem adding to graph: ', addr)
        if self.is_fee_addr(addr):
            self.graph_detail.edge(addr, 'bitsquare fees')
        elif self.get_addr_owner(addr) != '':
            self.graph_detail.edge(addr, self.get_addr_owner(addr))
        elif self.is_lock_addr(addr):
            addr_txt = 'intermediate ' + addr
        # mark as handled
        self.handled_addresses.add(addr)
        # explore further
        if depth > 0 and not self.is_fee_addr(addr):
            history = []
            try:
                history = self.ledger.history(addr)
            except:
                print('failed to get history for: ', addr)
            for tx in history:
                self.handle_tx(tx, depth - 1)

    def handle_tx(self, txid, depth = 3):
        if depth <= 0:
            return
        if txid in self.handled_transactions:
            return
        self.handled_transactions.add(txid)

        tx = self.ledger.load_tx(txid)
        if self.is_offer_fee_tx(tx):
            tx_name = 'offer_fee ' + txid 
        elif self.is_taker_fee_tx(tx):
            tx_name = 'taker_fee ' + txid 
        elif self.is_deposit_tx(tx):
            tx_name = 'deposit ' + txid
        elif self.is_payout(tx):
            tx_name = 'payout ' + txid
        else:
            tx_name = txid
        self.graph_detail.node(tx_name, shape='rectangle')

        for inp in tx.txs_in:
            addr = inp.bitcoin_address()
            if addr != '(unknown)':
                self.handle_address(addr, depth)
                previous_tx = self.ledger.load_tx(pycoin.serialize.b2h_rev(inp.previous_hash))
                prev_outp = previous_tx.txs_out[inp.previous_index]
                previous_coin_value = pycoin.convention.satoshi_to_btc(prev_outp.coin_value)
                self.graph_detail.edge(addr, tx_name, label=('%f' % previous_coin_value))
            
        for outp in tx.txs_out:
            addr = outp.bitcoin_address()
            if not addr is None:
                self.handle_address(addr, depth)
                coin_value = pycoin.convention.satoshi_to_btc(outp.coin_value)
                self.graph_detail.edge(tx_name, addr, label=('%f' % coin_value))
        
    def write_graph(self, filename):
        self.graph_detail.render(filename=filename)
	
# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    bs = bitsquare()

    bs.handle_tx("1af578e93f133e6b7999251b92073e44e360bb73219cf1c310a242e68133859b", 1) # offer fee
    bs.handle_tx("f73b9555ce5c06b05653e35d148e9ebd5abc348736b9b64c811183abdea2c6a1", 1) # taker fee
    bs.handle_tx("5312737afa52b04bce443266e57e26567afc7903c171733dc54540f325d4f512", 1) # deposit transaction
    bs.handle_tx("efac648ac2c6fb8d00856a283e25850362fbcf4ab4f6f50abd57146aec60e6ff", 1) # payout transaction

#    bs.process_known_people()

    filename = "/tmp/bitsquare_analysis"
    bs.write_graph(filename)

    subprocess.call(["eog", filename + '.svg'])
    


