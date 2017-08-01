#!/bin/bash

echo "Welcome to Slug Scrob"
echo
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/slug_scrob/

args=("$@")
python ./main.py "${args[0]}" "${args[1]}"

cd ..
echo
echo "Have a nice life"
