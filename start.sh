#!/bin/bash
export PYTHON_EGG_CACHE=/var/www/iat/.python-eggs
cd $1
source working-env/bin/activate
exec python ecomap_start.py $2
