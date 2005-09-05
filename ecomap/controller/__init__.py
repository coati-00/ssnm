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
        'sessionFilter.storageType' : "ram",
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


class Eco(EcoControllerBase):
    # enable filtering to disable post filtering on the postTester funcion
    _cpFilterList = [ DisablePostParsingFilter() ]
    
    def index(self):
        # import pdb; pdb.set_trace()
        return self.template("index.pt",{})
        #return "<h1>This is the main page</h1><p><a href='login'>Click here</a> to log in</p>"

    index.exposed = True

    def breakredirect(self):
        cherrypy.response.body = ["goodbye cruel world"]
        cherrypy.response.sendResponse = True
        return httptools.redirect("/index")
        # return cherrypy.response.body

    breakredirect.exposed = True
    
    
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
                            responseData = "<data><response>OK</response>" + thisEcomap.flashData + "</data>"
                        elif action == "save":
                            #if this is your ecomap, you can save it, otherwise, youre out of luck
                            if thisEcomap.owner.uni == sessionUni:
                                thisEcomap.flashData = dataNode
                                #want to check if this actually saves so i can REALLY return an OK
                                #if it doesn't save, return NOT OK
                                responseData = "<data><response>OK</response></data>"
                            else:
                                responseData = "<data><response>You do not own this ecomap</response></data>"
                            
                        else:
                            print "unknown data action"
                            responseData = "<data><response>Unknown data action</response></data>"
                        print thisEcomap.description
                    else:
                        responseData = "<data><response>Not your ecomap and not public</response></data>"
                        print "not your ecomap and not public"
                else:
                    responseData = "<data><response>Not a valid ecomap id</response></data>"
                    print "not a valid ecomap id"
            else:
                responseData = "<data><response>Not a valid session you little hacker</response></data>"
                print "not a valid session, you little hacker"
        

        return responseData
        
        print ticketid
        print ecoid
        #print dataNode
        #return postData
        
        #return "OK"
        
        #fetchEcomap = Ecomap.get(id)
        
        #return fetchEcomap.description
        #xml = "<response>OK</response>"
        
        #return xml
        #return "<xml><data>" + kwargs + "</data></xml>"
        
    flashConduit.exposed = True
    

    def postTester(self, **kwargs):
        """
        test the DisablePostParsingFilter -
        when we just want to get at the postdata,
        we can't let stdin be read, since we can't seek back to the beginning
        """
        # import pdb; pdb.set_trace()
        postLength = int(cherrypy.request.headerMap.get('Content-Length',0))
        postData = cherrypy.request.rfile.read(postLength) 
        return postData
    
    postTester.exposed = True

    def myList(self):
        # import pdb; pdb.set_trace()

        uni = cherrypy.session.get(UNI_PARAM, None)

        if uni:
            myEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == uni), orderBy=['name'])]
            publicEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni != uni, Ecomap.q.public == True), orderBy=['name'])]
            for e in myEcos:
                e.createdStr = e.created.strftime("%m/%d/%Y")
                e.modifiedStr = e.modified.strftime("%m/%d/%Y")
            return self.template("list_ecomaps.pt",{'myEcomaps' : myEcos, 'publicEcomaps' : publicEcos})
        else:
            #No user logged in
            return httptools.redirect("/")

    myList.exposed = True

    def login(self,**kwargs):
        ticket_id = kwargs.get('ticketid', "")
        self.BASE_URL = cherrypy.request.base + "/login"

        if ticket_id == "":
            import urllib
            destination = urllib.quote(self.BASE_URL)
            url = "https://wind.columbia.edu/login?destination=%s&service=cnmtl_full_np" % destination
            return httptools.redirect(url)
        else:
            
            (success,uni,groups) = validate_wind_ticket(ticket_id)
            if int(success) == 0:
                return uni # UNI is error message "WIND authentication failed. please try again or report this as a bug."

            #This is for authorization later from flash to forbid people from
            #invoking the ecomap with an id param to read anyone's ecomap
            cherrypy.session[AUTH_TICKET_PARAM] = ticket_id

            cherrypy.session[UNI_PARAM] = uni
            cherrypy.session['Group'] = groups

            user = get_or_create_user(uni)
            print cherrypy.session[UNI_PARAM]

            return httptools.redirect("/myList") #"success!! %s logged in.  <a href='/myList'>click here</a> to go to list of ecomaps" % uni

    login.exposed = True
    
    def loginB(self,**kwargs):
        cherrypy.session[UNI_PARAM] = 'kfe2102'
        cherrypy.session[AUTH_TICKET_PARAM] = 'TICKET!!!'
        return httptools.redirect("/myList")
        
    loginB.exposed = True


    def create_ecomap_form(self):
        defaults = {'name' : "x", 'description' : "y"}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("create_ecomap.pt",{}))
        output = parser.text()
        parser.close()
        return output

    create_ecomap_form.exposed = True


    def create_ecomap(self,name="",description=""):

        es = EcomapSchema()

        try:
            ownerID = Ecouser.select(Ecouser.q.uni == cherrypy.session[UNI_PARAM])[0].id
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
        #try:
            action = kwargs['action']
            if type(kwargs['ecomap_id']) is str:
                itemList = [int(kwargs['ecomap_id'])]
            elif type(kwargs['ecomap_id']) is list:
                itemList = [k for k in kwargs['ecomap_id']]
            else:
                output = "error - unknown argument type"

            if action == 'delete':
                for item in itemList:
                    thisItem = Ecomap.get(item)
                    thisItem.destroySelf()
            elif action == 'share':
                es = EcomapSchema()
                for item in itemList:
                    thisItem = Ecomap.get(item)
                    thisItem.public = not thisItem.public

            return httptools.redirect("/myList")

        #except:
        #   return "no arguments"

    update.exposed = True



class EcomapController(EcoControllerBase):

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
        return self.template("view_ecomap.pt",{'ecomap' : self.ecomap})
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