#!/usr/bin/env python

""" runs quip

starts up cherrypy based on the specified mode
"""
import sys
sys.path.append(".")
import ecomap.config as config

config.MODE = 'production'

import ecomap.controller as controller

def start(initOnly = 0):
    controller.start(initOnly)



