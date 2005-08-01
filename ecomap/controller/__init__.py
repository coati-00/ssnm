from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL

from cherrypy.lib import httptools
import cherrypy
import sys
import StringIO
import cgitb
import formencode
from formencode import validators
from formencode import htmlfill

DEBUG = True

class EcomapControllerBase(CherryTAL):
    _template_dir = "view"

    def referer(self):
        return cherrypy.request.headerMap.get('Referer','/')

    def _cpOnError(self):
        err = sys.exc_info()
        if DEBUG:
            sio = StringIO.StringIO()
            hook = cgitb.Hook(file=sio)
            hook.handle(info=err)            
            cherrypy.response.headerMap['Content-Type'] = 'text/html'
            cherrypy.response.body = [sio.getvalue()]
        else:
            # Do something else here.
            cherrypy.response.body = ['Error: ' + str(err[0])]

class EcomapController(EcomapControllerBase):
    def index(self):
        return self.template("list_applications.pt",{'ecomaps' : [e for e in Ecomap.select()]})
    index.exposed = True


    
        
