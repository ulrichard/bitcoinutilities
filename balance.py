#! /usr/bin/python
# Show the current balances

import accounts, bitcoinaverage, bitcoincharts
import locale, datetime, string

	
# test code
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')

    priceCHF = bitcoinaverage.bitcoinaverage('CHF').get_avg(datetime.date.today() - datetime.timedelta(days=1))
    priceUSD = bitcoincharts.bitcoincharts('bitstampUSD').last_close()

    acc = accounts.accounts('accounts.json')
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



