""" configuration for the app

 looks in the specified mode section for a config option
 if it doesn't find it there, it looks in the default 'kurt' mode"""

import ConfigParser

c = ConfigParser.ConfigParser()
c.read("ecomap/config/ecomap.conf")

MODE = "development"

def param(param):
    try:
        return c.get(MODE,param)
    except ConfigParser.NoOptionError:
        return c.get("kurt",param)