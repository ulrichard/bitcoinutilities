#! /bin/sh

#!/bin/bash
FILES=~/.electrum/wallets/*
for f in $FILES
do
  echo "Processing $f file..."
  electrum getbalance -w $f 
done
