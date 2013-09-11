#!/bin/bash
cd $1
source ve/bin/activate
exec python ecomap_start.py $2
