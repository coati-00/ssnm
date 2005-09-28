from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL
from ecomap.helpers import EcomapSchema
import ecomap.config as config
from DisablePostParsingFilter import DisablePostParsingFilter

from cherrypy.lib import httptools
from mx import DateTime
import cherrypy
import sys
import StringIO
import cgitb
import formencode
from formencode import validators
from formencode import htmlfill
from xml.dom.minidom import parseString

DEBUG = True

UNI_PARAM = "UNI"
AUTH_TICKET_PARAM = "auth_ticket"

def start(initOnly=False):
    environment = "development"
    if config.MODE == "production":
        environment = "production"

    #environment = "production"

    cherrypy.root             = Eco()
    cherrypy.root.ecomap      = EcomapController()

    cherrypy.config.update({
        'global' : {
        'server.socketPort' : int(config.param('socketPort')),
        'server.threadPool' : int(config.param('threadPool')),
        'server.environment' : environment,
        'sessionFilter.on' : True,
        'sessionFilter.storageType' : config.param('sessionStorageType'),
        'sessionFilter.storagePath' : config.param('storagePath'),
        },
        '/css' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('css')},
        '/images' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('images')},
        '/flash' : {'staticFilter.on' : True, 'staticFilter.dir' : config.param('flash')},
        })
    cherrypy.server.start(initOnly=initOnly)



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

from ecomap.controller.WindLoginFilter import WindLoginFilter

class Eco(EcoControllerBase):
    # enable filtering to disable post filtering on the postTester funcion
    _cpFilterList = [ DisablePostParsingFilter(),
                      WindLoginFilter(after_login="/myList",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]
    
    def index(self):
        # import pdb; pdb.set_trace()
        return self.template("index.pt",{})

    index.exposed = True

    def flashConduit(self,HTMLid="",HTMLticket=""):
        #import pdb; pdb.set_trace()
        
        #First, check to make sure there's a session established
        sessionUni = cherrypy.session.get(UNI_PARAM, None)
        sessionTicket = cherrypy.session.get(AUTH_TICKET_PARAM, None)
        
        if not sessionUni and sessionTicket:
            responseData = "<response>Session error</response>"

        else:
        
            postLength = int(cherrypy.request.headerMap.get('Content-Length',0))
            postData = cherrypy.request.rfile.read(postLength) 
    
            #postData is going to have a ticket and an id to parse out
    
            try:
                doc = parseString(postData)
            except:
                raise ParseError
                
            root = doc.getElementsByTagName("data")[0]
            
            #Check this data for reasonable stuff coming in
            if root.getElementsByTagName("ticket")[0].hasChildNodes():
                ticketid = root.getElementsByTagName("ticket")[0].firstChild.nodeValue
            else:
                ticketid = ""
            if root.getElementsByTagName("id")[0].hasChildNodes():
                ecoid = root.getElementsByTagName("id")[0].firstChild.nodeValue
            else:
                ecoid = ""
            if root.getElementsByTagName("action")[0].hasChildNodes():
                action = root.getElementsByTagName("action")[0].firstChild.nodeValue
            else:
                action = ""
            dataNode = root.getElementsByTagName("persons")[0].toxml()
            
            if ticketid == sessionTicket:
                #tickets match, so the session is valid
                if not ecoid == "":
                    thisEcomap = Ecomap.get(ecoid)
                    if thisEcomap.public or thisEcomap.owner.uni == sessionUni:
                        if action == "load":
                            print "load into flash: " + thisEcomap.flashData
                            if thisEcomap.owner.uni == sessionUni:
                                responseData = "<data><response>OK</response><isreadonly>false</isreadonly><name>" + thisEcomap.name + "</name><description>" + thisEcomap.description + "</description>" + thisEcomap.flashData + "</data>"
                            else:
                                #send it in as read only
                                responseData = "<data><response>OK</response><isreadonly>true</isreadonly><name>" + thisEcomap.name + "</name><description>" + thisEcomap.description + "</description>" + thisEcomap.flashData + "</data>"
                        elif action == "save":
                            #if this is your ecomap, you can save it, otherwise, youre out of luck
                            if thisEcomap.owner.uni == sessionUni:
                                if root.getElementsByTagName("name")[0].hasChildNodes():
                                    ecoName = root.getElementsByTagName("name")[0].firstChild.nodeValue
                                else:
                                    ecoName = ""
                                if root.getElementsByTagName("description")[0].hasChildNodes():
                                    ecoDescription = root.getElementsByTagName("description")[0].firstChild.nodeValue
                                else:
                                    ecoDescription = ""
                                thisEcomap.flashData = dataNode
                                thisEcomap.name = ecoName
                                thisEcomap.description = ecoDescription
                                thisEcomap.modified = DateTime.now()
                                #want to check if this actually saves so i can REALLY return an OK
                                #if it doesn't save, return NOT OK
                                responseData = "<data><response>OK</response></data>"
                            else:
                                responseData = "<data><response>This is not your ssnm</response></data>"
                        else:
                            print "unknown data action"
                            responseData = "<data><response>Unknown data action</response></data>"
                        print thisEcomap.description
                    else:
                        responseData = "<data><response>This is not your ssnm and it is not public</response></data>"
                        print "not your ecomap and not public"
                else:
                    responseData = "<data><response>That ssnm id does not exist</response></data>"
                    print "not a valid ecomap id"
            else:
                responseData = "<data><response>Your session may have timed out</response></data>"
                print "not a valid session, you little hacker"
        

        return responseData
        
        print ticketid
        print ecoid
       
    flashConduit.exposed = True
    
    def myList(self):
        #import pdb; pdb.set_trace()
        print cherrypy._sessionMap
        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')

        if uni == None and config.MODE == "regressiontest":
            uni = "foo"

        if uni:
            myEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == uni), orderBy=['name'])]
            publicEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni != uni, Ecomap.q.public == True), orderBy=['name'])]
            for e in myEcos:
                e.createdStr = e.created.strftime("%m/%d/%Y")
                e.modifiedStr = e.modified.strftime("%m/%d/%Y")
            return self.template("list_ecomaps.pt",{'loginName' : loginName, 'myEcomaps' : myEcos, 'publicEcomaps' : publicEcos})
        else:
            #No user logged in
            return httptools.redirect("/logout")

    myList.exposed = True

    def logout(self,**kwargs):
        return self.template("logout.pt",{})
    logout.exposed = True    

    def create_ecomap_form(self):
        uni = cherrypy.session.get(UNI_PARAM, None)
        
        defaults = {'name' : "", 'description' : ""}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("create_ecomap.pt",{}))
        output = parser.text()
        parser.close()
        return output

    create_ecomap_form.exposed = True


    def create_ecomap(self,name="",description=""):

        es = EcomapSchema()

        uni = cherrypy.session.get(UNI_PARAM,None)
        if uni == None:
            if config.MODE == "regressiontest":
                uni = "foo"
            else:
                return httptools.redirect("/logout")    
        try:
            ownerID = Ecouser.select(Ecouser.q.uni == uni)[0].id
            d = es.to_python({'name' : name, 'description' : description, 'owner' : ownerID})
            a = Ecomap(name=d['name'],description=d['description'],owner=d['owner'])
            return httptools.redirect("/myList")
        except formencode.Invalid, e:
            defaults = {'name' : name, 'description' : description}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("create_ecomap.pt",{}))
            output = parser.text()
            parser.close()
            return output

    create_ecomap.exposed = True

    def update(self,**kwargs):
        #import pdb; pdb.set_trace()
        action = kwargs['action']
        #make sure at least one checkbox was selected
        ecomapList = kwargs.get('ecomap_id',None)
        if ecomapList:
            if type(ecomapList) is str:
                itemList = [int(kwargs['ecomap_id'])]
            elif type(kwargs['ecomap_id']) is list:
                itemList = [k for k in kwargs['ecomap_id']]
            else:
                output = "error - unknown argument type"
        else:
            return httptools.redirect("/myList")

        if action == 'Delete Selected':
            for item in itemList:
                thisItem = Ecomap.get(item)
                thisItem.destroySelf()
        elif action == 'share':
            es = EcomapSchema()
            for item in itemList:
                thisItem = Ecomap.get(item)
                thisItem.public = not thisItem.public

        return httptools.redirect("/myList")

    update.exposed = True



class EcomapController(EcoControllerBase):
    _cpFilterList = [WindLoginFilter(after_login="/myList",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]
    def index(self):
        return self.template("list_ecomaps.pt",{'ecomaps' : [e for e in Ecomap.select()]})
    index.exposed = True


    def default(self,ecomap_id,*args,**kwargs):
        # import pdb; pdb.set_trace()
        ecomap_id = int(ecomap_id)
        try:
            self.ecomap = Ecomap.get(ecomap_id)

            if len(args) == 0:
                return self.view_ecomap(**kwargs)
            action = args[0]
    
            dispatch = {
                'delete' : self.delete,
                'edit_form' : self.edit_form,
                'edit' : self.edit,
                'flash' : self.flash,
                }
            if dispatch.has_key(action):
                return dispatch[action](**kwargs)
        except:
            print "SQL error - no ecomap for that id"
            return httptools.redirect("/myList")

    default.exposed = True

    def edit_form(self):
        defaults = {'name' : self.ecomap.name, 'description' : self.ecomap.description}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("edit_ecomap.pt",{'ecomap' : self.ecomap}))
        output = parser.text()
        parser.close()
        return output

    def edit(self,name="",description=""):
        es = EcomapSchema()
        try:
            d = es.to_python({'name' : name, 'description' : description, 'owner' : self.ecomap.ownerID})
            self.ecomap.name = d['name']
            self.ecomap.description = d['description']
            self.ecomap.modified = DateTime.now()
            return httptools.redirect("/ecomap/" + str(self.ecomap.id) + "/")
    
        except formencode.Invalid, e:
            defaults = {'name' : name, 'description' : description}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("edit_ecomap.pt",{'ecomap' : self.ecomap}))
            output = parser.text()
            parser.close()
            return output

    def view_ecomap(self,**kwargs):
        data = {
            'ecomap' : self.ecomap,
            'id' : self.ecomap.id,
            'ticket' : cherrypy.session.get(AUTH_TICKET_PARAM,None),
            'myName' : cherrypy.session.get('fullname',""),
            }
        return self.template("view_ecomap.pt",data)
    #ecomap.exposed = True


    def delete(self,confirm=""):
        #if confirm == "ok":
            self.ecomap.destroySelf()
            #cherrypy.session['message'] = "application deleted"
            return httptools.redirect("/myList")
        #else:
        #    return self.template("delete_ecomap.pt",{})

    def flash(self):
        flashData = {
            'id' : self.ecomap.id,
            'ticket' : cherrypy.session.get(AUTH_TICKET_PARAM,None),
            }
        return self.template("flash.pt",flashData)
