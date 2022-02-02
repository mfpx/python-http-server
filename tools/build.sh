#!/bin/bash

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac

if [ "$machine" == "Linux" ] || [ "$machine" == "Mac" ]
then
    echo "Found \"${machine}\", continuing..."

    if [ -z "$1" ]
    then
        echo "PyInstaller log level set to \"TRACE\" - expect around 10k lines of output"
        loglevel="TRACE"
    else
        echo "PyInstaller log level set to \"$1\""
        loglevel=$1
    fi

    echo "Building targets for server"
    pyinstaller --log-level "$loglevel" -n "server" --clean --noconfirm server.py # Build server.py

    echo "Building targets for converter"
    pyinstaller --log-level "$loglevel" -n "converter" --clean --noconfirm converter.py # Build converter.py - will be removed in the future

    printf "Done!\nCompiled binaries can be found in \"dist\" directory\n"
else
    printf "Found %s!\nBuilds have only been tested on Linux and OSX!\n" "$machine"
fi