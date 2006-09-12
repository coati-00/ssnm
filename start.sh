#!/bin/bash
cd $1
source working-env/bin/activate
./ecomap_start.py -m $2 &
echo $! > /tmp/ecomap/$2.pid
wait $!
