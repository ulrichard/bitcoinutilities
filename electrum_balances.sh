#! /bin/bash

total=0
prices=$(curl ${CURL_PROXY} -H "X-CMC_PRO_API_KEY: 20063e5b-7005-4c14-8e21-9f14ffe3c21f" -H "Accept: application/json" -d "start=1&limit=1000&convert=CHF" -G https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest 2> /dev/null)
btcchf=$(echo $prices | jq -r '.data[] | select(.symbol=="BTC") | .quote.CHF.price')
echo BTC-CHF: $btcchf

# electrum daemon -d

printf "%25s\t%10s\t%8s\n" file BTC CHF

for f in ~/.electrum/wallets/*
do
    if [ -f "$f" ]
    then
        electrum load_wallet -w $f > /dev/null
        balance=$(electrum getbalance -w $f | jq -r '.confirmed')
        chf=$(echo "$balance $btcchf * p" | dc)
        #printf "%25s\t%.8f\t%'.2f\n" $(basename $f) $balance $chf
        printf "%25s\t%s\t%s\n" $(basename $f) $balance $chf

        if [[ "$(basename $f)" != "_"* ]] 
        then
            total=$(echo "$total $balance + p" | dc)
        fi
    fi
done

# electrum stop

chf=$(echo "$total $btcchf * p" | dc)
#printf "\n%25s\t%.8f\t%'.2f\n" total $total $chf
printf "\n%25s\t%s\t%s\n" total $total $chf
echo $chf
