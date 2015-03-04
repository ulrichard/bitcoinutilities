#! /usr/bin/python
# Show the current balances

import bitcoincharts, bitcoinaverage, accounts

import httplib2
import json
import locale, string, csv, datetime, os
import StringIO
import dateutil.parser
import matplotlib.pyplot as plt
from pylab import *

		
if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    addresses = []
    ledgers = {}
    now = datetime.date.today()
#	now = datetime.date(2013, 12, 31)
    priceCHF = bitcoincharts.bitcoincharts('mtgoxCHF').bid()
    priceUSD = bitcoincharts.bitcoincharts('bitstampUSD').last_close()
    btcavgCHF = bitcoinaverage.bitcoinaverage('CHF')
    btcavgUSD = bitcoinaverage.bitcoinaverage('USD')
    priceCHFyesterday = btcavgCHF.get_avg(datetime.date.today() - datetime.timedelta(days=1))

    homedir = os.environ['HOME']
    dirs = [homedir + '/Dokumente/BitCoin', homedir + '/.bitcoin', '.']
    acc = None
    for d in dirs:
        print d
        if os.path.isfile(d + '/mining.json'):
            acc = accounts.accounts(d + '/mining.json')
            break
    for i in range(len(acc.addresses)):
        person = acc.addresses[i]
        name = person.items()[0][0]
        for j in range(len(person.items()[0][1])):
            addr = person.items()[0][1][j].items()[0][1]
            addresses.append(addr)

    day = now
    for addr in reversed(addresses):
        ledger = accounts.blockchain(addr, True)
        txs = ledger.get_transactions()
        ledgers[addr] = ledger
        dates = txs.keys()
        if len(dates):
            dates.sort()
            if dates[0] < day:
                day = dates[0]
        
    sum = 0
    sumday = 0

    csvwriter = csv.writer(open('earnings.csv', 'wb'), delimiter=',')
    row = ['day', 'val', 'valInCHFnow', 'valInUSDnow', 'valInCHFthen', 'priceCHFthen']
    csvwriter.writerow(row)
    days   = []
    values = []
    valday = []
    valuesPerMonth = {}
    valdayPerMonth = {}

    while day <= now:
    # ToDo : fetch the conversion for the day
        val = 0
        for addr in ledgers:
            ledger = ledgers[addr]
            txs = ledger.get_transactions()

            if(txs.has_key(day)):
                val += txs[day] / 100000000.0

        dailyCHF = btcavgCHF.get_avg(day)
        if dailyCHF == 0:
            dailyCHF = 0.9 * btcavgUSD.get_avg(day)

        print day, ' ', \
            string.rjust(locale.currency(val, grouping=True)[4:], 6), 'XBT  ', \
            string.rjust(locale.currency(val * priceCHFyesterday, grouping=True)[4:], 7), 'CHF  ', \
            string.rjust(locale.currency(val * priceUSD, grouping=True)[4:], 7), 'USD', \
            string.rjust(locale.currency(val * dailyCHF, grouping=True)[4:], 7), 'CHF' 

        row = [day, val, val * priceCHF, val * priceUSD, val * dailyCHF, dailyCHF]
        csvwriter.writerow(row)

        days.append(day)
        values.append(val)
        valday.append(val * dailyCHF)
        sum += val
        sumday += val * dailyCHF

        month = '%d-%02d' % (day.year, day.month)
        if not valuesPerMonth.has_key(month):
            valuesPerMonth[month] = 0
            valdayPerMonth[month] = 0
        valuesPerMonth[month] += val
        valdayPerMonth[month] += val * dailyCHF

        day += datetime.timedelta(days=1)



    plt.clf()
    plot(days, values, label = 'XBT')
    plt.legend(['XBT'])
    savefig('earnings.png', format='png')

    months = valuesPerMonth.keys()
    months.sort()
    for month in months:
        print month, ' ', \
        string.rjust(locale.currency(valuesPerMonth[month], grouping=True)[4:], 6), 'XBT ', \
        string.rjust(locale.currency(valdayPerMonth[month], grouping=True)[4:], 9), 'CHF '

    print 'earned between ', dates[0], ' and ', dates[len(dates) - 1], ' : ', string.rjust(locale.currency(sum, grouping=True)[4:], 6), 'XBT'
    print 'at yesterdays exchange rate  ', \
        string.rjust(locale.currency(sum * priceCHFyesterday, grouping=True)[4:], 7), 'CHF ', \
        string.rjust(locale.currency(sum * priceUSD, grouping=True)[4:], 7), 'USD'

    print 'at daily exchange rate   ', string.rjust(locale.currency(sumday, grouping=True)[4:], 6), 'CHF'

