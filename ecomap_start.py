#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
from os.path import *

try:
    import sys

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m","--mode", dest="mode", help="specify the mode", default="dev",metavar="MODE")

    (options, args) = parser.parse_args()
except AttributeError:
    # mod_python has no sys.argv accessible
    pass

from ecomap.controllers import build_controllers

build_controllers()

if __name__ == "__main__":
    cherrypy.config.update(file=join(dirname(__file__),options.mode + ".cfg"))
    cherrypy.server.start()

def mp_setup():
    '''
    mpcp.py looks for this method for CherryPy configs but our *.cfg files handle that.
    '''
    cherrypy.config.update(file=join(dirname(__file__),"prod.cfg"))

