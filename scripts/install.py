#!/usr/bin/env python

""" installs ecomap

sets up the database tables and puts in default settings.

expects that the database specified in the dsn has been created
"""
import sys
sys.path.append(".")
sys.path.append("..")

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m", "--mode", dest="mode", help="specify the mode", default="default", metavar="MODE")
parser.add_option("-d", "--drop", dest="drop", help="drop existing tables", default=False, action="store_true")

(options, args) = parser.parse_args()

from ecomap.helpers import *

if options.drop:
    dropTables()

createTables()
user = Ecouser(uni="kfe2102",firstname="Kurt",lastname="Eldridge",securityLevel=1)
