#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy, os, turbogears
from os.path import *
import sys

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    turbogears.update_config(configfile=sys.argv[1],
        modulename="ecomap.config")
elif exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile="dev.cfg",
        modulename="ecomap.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="ecomap.config")

from ecomap.controllers import build_controllers


turbogears.start_server(build_controllers())







