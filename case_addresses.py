#! /usr/bin/python
# Find the current balances for known addresses

import blockchain_info
import json
import locale, os
import pycoin.key.BIP32Node, pycoin.key.Key, pycoin.key.electrum
from pycoin.tx.pay_to import address_for_pay_to_script, build_hash160_lookup, build_p2sh_lookup, ScriptMultisig


class case_addresses:
    def __init__(self, filename):
        locale.setlocale(locale.LC_ALL, '')
        self.addresses = json.load(open(filename))

    def list_addresses(self, filterName = ''):
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

                    for k in range(4): # device (0), web (1) or exchange (2) for case hardware wallet. idx (3) used for non-case
                        for j in range(2): # receive (0) and change (1) addresses
                            gap = 0
                            found = False
                            for i in range(99999):
                                if k == 3:   # regular
                                    keypath = "%d/%d.pub" % (j, i)
                                else:        # case
                                    keypath = "%d/%d/%d.pub" % (k, j, i)
                                #print(keypath)
                                sub0 = kk0.subkey_for_path(keypath).sec()
                                sub1 = kk1.subkey_for_path(keypath).sec()
                                sub2 = kk2.subkey_for_path(keypath).sec()
                                if k == 3: # regular
                                    sub = sorted([sub0, sub1, sub2])
                                else:      # case
                                    sub = [sub0, sub1, sub2]
                                underlying_script = ScriptMultisig(n=2, sec_keys=[sub[0], sub[1], sub[2]]).script()
                                addr = address_for_pay_to_script(underlying_script, netcode="BTC")
                                ledger = blockchain_info.blockchain(addr, False)
                                bal  = ledger.balance()
                                if ledger.tx_count != 0:
                                    found = True
                                if found:
                                    print desc, i, j, k, addr, bal
                                if bal == 0:
                                    if 0 == ledger.tx_count():
                                        gap += 1
                                        if gap > 20:
                                            break

# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    homedir = os.environ['HOME']
    acc = case_addresses(homedir + '/Dokumente/BitCoin/accounts.json')
    acc.list_addresses()
