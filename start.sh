#!/bin/bash
cd $1
source working-env/bin/activate
./ecomap_start.py -m $2
