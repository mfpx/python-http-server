#!/bin/bash

if command -v pip3 &> /dev/null
then
    echo "pip3 exists"
    if ! pip3 install -r requirements.txt
    then
        echo "pip3 failed to install all required packages, aborting..."
        exit 1
    fi
elif command -v pip &> /dev/null
then
    echo "pip3 does not exist, attempting pip"
    if ! pip install -r requirements.txt
    then
        echo "pip failed to install all required packages, aborting..."
        exit 1
    fi
else
    echo "python package manager not found!"
    exit 1
fi