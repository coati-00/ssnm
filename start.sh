#!/bin/bash
cd $1
python workingenv.py -r requirements.txt working-env
source working-env/bin/activate
python mppath.py
