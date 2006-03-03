#!/usr/bin/env python

import sys
sys.path.append(".")
import ecomap.config as config

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m","--mode", dest="mode", help="specify the mode", default="kurt",metavar="MODE")

(options, args) = parser.parse_args()

config.MODE = options.mode

from ecomap.helpers import *
from ecomap.model   import *

import ecomap.controllers as controller
import cherrypy

controller.start()

