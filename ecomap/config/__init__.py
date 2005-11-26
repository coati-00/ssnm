""" configuration for the app

 looks in the specified mode section for a config option
 if it doesn't find it there, it looks in the 'default' mode"""

import ConfigParser,os.path

c = ConfigParser.ConfigParser()
c.read(os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__),"../config/ecomap.conf"))))

MODE = "development"

def param(param):
    try:
        return c.get(MODE,param)
    except ConfigParser.NoOptionError:
        return c.get("default",param)
