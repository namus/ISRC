#!/usr/bin/env bash

for file in *.py
do
echo "Running $file ..."
python $file
done
