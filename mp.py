#!/usr/bin/env python

import prodpath
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *
import sys, os

from ecomap.controllers import build_controllers

build_controllers()
def mp_setup():
    '''
    mpcp.py looks for this method for CherryPy configs but our *.cfg files handle that.
    '''
    host = os.environ.get('ECOMAP_HOST',"ssnm")
    static = ["css","images","flash","js"]
    for s in static:
        cherrypy.config.update({"/%s" % s : {"staticFilter.on" : True, "staticFilter.dir" : "static-%s/%s" % (host,s)}})
    
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))



