#!/usr/bin/env python

import sys
sys.path.append(".")

from ecomap.helpers import *
from ecomap.model   import *
import ecomap.controller as controller

import cherrypy

cherrypy.root             = controller.EcomapController()

cherrypy.config.update(file="config/ecomap.conf")
cherrypy.server.start()
