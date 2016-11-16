#! /usr/bin/python
# analyze a bitsquare transaction, starting from the taker fee transaction

import electrum_client
import locale, datetime, string, os, subprocess
import pycoin
import graphviz as gv


class bitsquare:
    def __init__(self, taker_fee_tx_id):
        locale.setlocale(locale.LC_ALL, '')
        self.taker_fee_tx_id = taker_fee_tx_id
        self.fee_addresses = ['1FdFzBazmHQxbUbdCUJwuCtR37DrZrEobu', '19PGJpBbHqmAWTkqX8NRdTnTRDvkBvqcSp']
        self.ledger = electrum_client.electrum_cli()
        self.taker_fee_tx = self.ledger.load_tx(taker_fee_tx_id)

    def write_graph(self, filename):
        g = gv.Digraph(format='svg')
        taker_fee_name = 'taker_fee ' + self.taker_fee_tx_id 
        tx_node = g.node(taker_fee_name)
        for inp in self.taker_fee_tx.txs_in:
            addr = inp.bitcoin_address()
            n = g.node(addr)
            previous_tx = self.ledger.load_tx(pycoin.serialize.b2h_rev(inp.previous_hash))
            prev_outp = previous_tx.txs_out[inp.previous_index]
            previous_coin_value = pycoin.convention.satoshi_to_btc(prev_outp.coin_value)
            g.edge(addr, taker_fee_name, label=('%f' % previous_coin_value))
        for outp in self.taker_fee_tx.txs_out:
            addr = outp.bitcoin_address()
            if addr in self.fee_addresses:
                addr = 'bitsquare fees'
            else:
                addr = 'taker ' + addr
            n = g.node(addr)
            coin_value = pycoin.convention.satoshi_to_btc(outp.coin_value)
            g.edge(taker_fee_name, addr, label=('%f' % coin_value))
        
        g.render(filename=filename)
	
# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    taker_fee_tx = "f73b9555ce5c06b05653e35d148e9ebd5abc348736b9b64c811183abdea2c6a1"
    bs = bitsquare(taker_fee_tx)
    bs.write_graph("/tmp/" + taker_fee_tx)

    subprocess.call(["inkscape", "/tmp/" + taker_fee_tx + ".svg"])
    


