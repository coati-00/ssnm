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

class EcoControllerBase(CherryTAL):
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

class Eco(EcoControllerBase):
    def index(self):
        return self.template("list_applications.pt",{'ecomaps' : [e for e in Ecomap.select()]})
    index.exposed = True

    def create_ecomap_form(self):
        defaults = {'name' : "x", 'description' : "y"}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("create_ecomap.pt",{}))
        output = parser.text()
        parser.close()
        return output
    
    create_ecomap_form.exposed = True


    def create_ecomap(self,name=u"",description=u""):
        
        es = EcomapSchema()
        try:
            #d = es.to_python({'name' : name, 'description' : description})
            #a = Ecomap(name=d['name'],description=d['description'])
            a = Ecomap(name=name,description=description,owner=1)
            #a = Ecomap(name,description)
            #cherrypy.session['message'] = "ecomap added"
            return httptools.redirect("/")
        except formencode.Invalid, e:
            return es.to_python({'name' : name, 'description' : description}) #e.unpack_errors()
            '''defaults = {'name' : name, 'description' : description}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("create_ecomap.pt",{}))
            output = parser.text()
            parser.close()
            return output '''
            
    create_ecomap.exposed = True


class EcomapController(EcoControllerBase):

    def index(self):
        return self.template("list_applications.pt",{'ecomaps' : [e for e in Ecomap.select()]})
    index.exposed = True


    def default(self,ecomap_id,*args,**kwargs):
        ecomap_id = int(ecomap_id)
        self.ecomap = Ecomap.get(ecomap_id)
        if len(args) == 0:
            return self.view_ecomap(**kwargs)
        action = args[0]

        dispatch = {
            'delete' : self.delete,
            }
        if dispatch.has_key(action):
            return dispatch[action](**kwargs)
    default.exposed = True


    def view_ecomap(self,**kwargs):
        return self.template("view_ecomap.pt",{'ecomap' : self.ecomap})
    #ecomap.exposed = True
    
    
    def delete(self,confirm=""):
        #if confirm == "ok":
            self.ecomap.destroySelf()
            #cherrypy.session['message'] = "application deleted"
            return httptools.redirect("/")
        #else:
        #    return self.template("delete_ecomap.pt",{})
        
        
        
        
        