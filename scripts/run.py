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

import ecomap.controller as controller
import cherrypy

environment = "development"
if config.MODE == "production":
    environment = "production"

cherrypy.root             = controller.Eco()
cherrypy.root.ecomap      = controller.EcomapController()

cherrypy.config.update({
    'global' : {
    'server.socketPort' : int(config.param('socketPort')),
    'server.threadPool' : int(config.param('threadPool')),
    'server.environment' : environment,
    },
    '/css' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('css')},
    '/images' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('images')},
    })
cherrypy.server.start()
