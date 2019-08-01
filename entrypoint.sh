#!/usr/bin/env bash

# Set mic volume
amixer -c 1 sset Mic 100%;

# Start the script
python3 audioServer.py;