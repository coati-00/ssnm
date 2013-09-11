import sys
from cherrypy.lib.filter import basefilter
import cherrypy

class DisablePostParsingFilter(basefilter.BaseFilter):
    def beforeRequestBody(self):
        if cherrypy.request.path.endswith("/flashConduit"):
            cherrypy.request.processRequestBody = False
