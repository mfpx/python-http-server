#!/bin/bash

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac

if [ "$machine" == "Linux" ]
then
    echo "Found \"${machine}\", continuing..."
    pyinstaller --log-level TRACE -n "server" --clean --noconfirm server.py # Build server.py
    pyinstaller --log-level TRACE -n "converter" --clean --noconfirm converter.py # Build converter.py - will be removed in the future
    # TRACE used for debugging build issues
    printf "Done!\nCompiled binaries can be found in \"dist\" directory"
else
    echo "Builds have only been tested on Linux!"
fi