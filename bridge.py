#!/usr/bin/env python
import os
os.chdir(os.path.normpath(os.path.dirname(__file__)))
import cherrypy
from modcherry import *

import sys
sys.path.append(".")
import ecomap.config as config

config.MODE = 'production'

import ecomap.controller as controller
controller.start(1)



