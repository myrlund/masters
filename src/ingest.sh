#!/bin/bash

echo "--- Updating raw data files."
../data/update.sh

echo "--- Loading new data into database."
./load.py

echo "--- Cleaning data, step 1."
./clean.py
