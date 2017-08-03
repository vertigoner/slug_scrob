#!/bin/bash

echo "Welcome to Slug Scrob"
echo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/../slug_scrob/

args=("$@")
python3.5 ./main.py "${args[0]}" "${args[1]}"

echo
echo "Have a nice life"
