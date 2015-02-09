#! /usr/bin/python
# Show the current balances

import accounts, bitcoinaverage, bitcoincharts
import locale, datetime, string, os

	
# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    priceCHF = bitcoinaverage.bitcoinaverage('CHF').get_avg(datetime.date.today() - datetime.timedelta(days=1))
    priceUSD = bitcoincharts.bitcoincharts('bitstampUSD').last_close()

    
    homedir = os.environ['HOME']
    dirs = [homedir + '/Dokumente/BitCoin', homedir + '/.bitcoin', '.']
    acc = None
    for d in dirs:
        print d
        if os.path.isfile(d + '/accounts.json'):
            acc = accounts.accounts(d + '/accounts.json')
            break
    balances = acc.balances()
    print(len(balances))
    for name in balances:
        addresses = balances[name]
        sum = 0
        for addr in addresses:
            sum += addresses[addr][0]

        print string.ljust(name, 22), '  ', \
            string.rjust(locale.currency(sum, grouping=True)[4:], 8), 'XBT  ', \
            string.rjust(locale.currency(sum * priceCHF, grouping=True)[4:], 10), 'CHF  ', \
            string.rjust(locale.currency(sum * priceUSD, grouping=True)[4:], 10), 'USD' 



