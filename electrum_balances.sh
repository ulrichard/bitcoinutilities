#! /bin/bash

total=0
btcchf=$(curl -s https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=CHF | jq -r '.[0].price_chf')
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
