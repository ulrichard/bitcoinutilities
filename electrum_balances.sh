#! /bin/bash

total=0
prices=$(curl ${CURL_PROXY} -H "X-CMC_PRO_API_KEY: 67cb5457-a155-47d8-8a36-1c81872b7509" -H "Accept: application/json" -d "start=1&limit=1000&convert=CHF" -G https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest 2> /dev/null)
btcchf=$(echo $prices | jq -r '.data[] | select(.symbol=="BTC") | .quote.CHF.price')
echo BTC-CHF: $btcchf

printf "%25s\t%10s\t%8s\n" file BTC CHF

for f in ~/.electrum/wallets/*
do
    if [ -f "$f" ]
    then
        electrum daemon load_wallet -w $f > /dev/null
        balance=$(electrum getbalance -w $f | jq -r '.confirmed')
        chf=$(echo "$balance $btcchf * p" | dc)
        printf "%25s\t%.8f\t%'.2f\n" $(basename $f) $balance $chf

        if [ "family_and_friends" != "$(basename $f)" ] && [  "Mirella" != "$(basename $f)" ]
        then
            total=$(echo "$total $balance + p" | dc)
        fi
    fi
done

chf=$(echo "$total $btcchf * p" | dc)
printf "\n%25s\t%.8f\t%'.2f\n" total $total $chf
echo $chf
