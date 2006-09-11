#!/bin/bash
cd $1
source working-env/bin/activate
python ecomap_start.py -m $2
