#! /usr/bin/python
# Find the current balances for known addresses

import blockchain_info, electrum_client
import json
import locale
import pycoin.key.BIP32Node, pycoin.key.Key, pycoin.key.electrum
from pycoin.tx.pay_to import address_for_pay_to_script, build_hash160_lookup, build_p2sh_lookup, ScriptMultisig


class accounts:
    def __init__(self, filename):
        locale.setlocale(locale.LC_ALL, '')
        self.addresses = json.load(open(filename))

    def get_balance(self, addr):
#        ledger = blockchain_info.blockchain(addr, False)
        ledger = electrum_client.electrum_cli()
        bal  = ledger.balance(addr)
        
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
                if len(addr) == 3:
                    # multisig deterministic hierarchical wallet
                    kk0 = pycoin.key.BIP32Node.BIP32Node.from_hwif(addr[0])
                    kk1 = pycoin.key.BIP32Node.BIP32Node.from_hwif(addr[1])
                    kk2 = pycoin.key.BIP32Node.BIP32Node.from_hwif(addr[2])

                    for k in range(5): # device (0), web (1) or exchange (2) for case hardware wallet. Regular non case: 2of3 (3), 3of3 (4)
                        for j in range(2): # receive (0) and change (1) addresses
                            gap = 0
                            for i in range(99999):
                                if k == 3 or k == 4:   # regular
                                    keypath = "%d/%d.pub" % (j, i)
                                else:        # case
                                    keypath = "%d/%d/%d.pub" % (k, j, i)
                                #print(keypath)
                                sub0 = kk0.subkey_for_path(keypath).sec()
                                sub1 = kk1.subkey_for_path(keypath).sec()
                                sub2 = kk2.subkey_for_path(keypath).sec()
                                if k == 3 or k == 4: # regular
                                    sub = sorted([sub0, sub1, sub2])
                                else:      # case
                                    sub = [sub0, sub1, sub2]
                                required_signatures = 3 if k == 4 else 2
                                underlying_script = ScriptMultisig(n=required_signatures, sec_keys=[sub[0], sub[1], sub[2]]).script()
                                addr = address_for_pay_to_script(underlying_script, netcode="BTC")
                                bal  = self.get_balance(addr)
                                #print desc, i, j, addr, bal
                                balance[name][addr] = [bal, '%s_%s_%d' % (desc, 'P' if 0 == j else 'Chg', i)]
                                if bal == 0:
                                    if 0 == ledger.tx_count():
                                        gap += 1
                                        if gap > 10:
                                            break
                elif len(addr) < 40:
                    # regular address
                    bal  = self.get_balance(addr)
                    balance[name][addr] = [bal, desc]
                elif 'xpub' == addr[0:4]:
                    # deterministic hierarchical public key
                    kk = pycoin.key.BIP32Node.BIP32Node.from_hwif(addr)
                    for j in range(2): # receive and change addresses
                        gap = 0
                        for i in range(99999):
                            keypath = "%d/%d.pub" % (j, i)
                            #print(keypath)
                            addr = kk.subkey_for_path(keypath).address()
                            #print i, j, addr
                            bal  = self.get_balance(addr)
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
                            bal  = self.get_balance(addr)
                            balance[name][addr] = [bal, '%s_%s_%d' % (desc, 'P' if 0 == j else 'Chg', i)]

        return balance

