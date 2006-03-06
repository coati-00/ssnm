from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL, site_root
from ecomap.helpers import EcomapSchema
import ecomap.config as config
from DisablePostParsingFilter import DisablePostParsingFilter

from cherrypy.lib import httptools
from mx import DateTime
import cherrypy
import sys, os.path
import StringIO
import cgitb
import formencode
from formencode import validators
from formencode import htmlfill
from xml.dom.minidom import parseString

DEBUG = True

UNI_PARAM = "UNI"
AUTH_TICKET_PARAM = "auth_ticket"
ADMIN_USERS = ("kfe2102","dm2150","ssw12")

def init_config():
    environment = "development"
    if config.MODE == "production":
        environment = "production"

    #environment = "production"

    cherrypy.root             = Eco()
    cherrypy.root.ecomap      = EcomapController()
    cherrypy.root.course      = CourseController()

    cherrypy.config.update({
        'global' : {
        'server.socketPort' : int(config.param('socketPort')),
        'server.threadPool' : int(config.param('threadPool')),
        'server.environment' : environment,
        'sessionFilter.on' : True,
        'sessionFilter.storageType' : config.param('sessionStorageType'),
        'sessionFilter.storagePath' : config.param('storagePath'),
        },
        '/css' : {'staticFilter.on' : True, 'staticFilter.dir' : os.path.join(site_root(),config.param('css'))},
        '/images' : {'staticFilter.on' : True, 'staticFilter.dir' : os.path.join(site_root(),config.param('images'))},
        '/flash' : {'staticFilter.on' : True, 'staticFilter.dir' : os.path.join(site_root(),config.param('flash'))},
        })


def start(initOnly=False):
    init_config()
    cherrypy.server.start(initOnly=initOnly)

def mp_setup(initOnly=False):
    config.MODE = "production"
    init_config()

class EcoControllerBase(CherryTAL):
    _template_dir = "ecomap/templates"

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

from WindLoginFilter import WindLoginFilter

class Eco(EcoControllerBase):
    # enable filtering to disable post filtering on the postTester funcion
    _cpFilterList = [ DisablePostParsingFilter(),
                      WindLoginFilter(after_login="/course",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]

    @cherrypy.expose()
    def index(self):
        # import pdb; pdb.set_trace()
        return self.template("index.pt",{})

    #legacy redirect for flash
    @cherrypy.expose()
    def myList(self):
        raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
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
                    # if this is public or it's yours or Susan, Debbie or I am logged in, allow the data to Flash
                    if thisEcomap.public or thisEcomap.owner.uni == sessionUni or sessionUni in ADMIN_USERS:
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

    @cherrypy.expose()
    def logout(self,**kwargs):
        return self.template("logout.pt",{})

    @cherrypy.expose()
    def create_course_form(self):
        uni = cherrypy.session.get(UNI_PARAM, None)

        defaults = {'description' : "", 'instructor' : ""}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("create_course.pt",{'allInstructors' : [i for i in Ecouser.select()]}))
        parser.close()
        output = parser.text()
        return output

    @cherrypy.expose()
    def create_course(self,description="",instructor="",students=""):
        #import pdb; pdb.set_trace()

        es = CourseSchema()

        # MUST sanitize this comma delimited list
        uniList = students.split(",")
        uniList.sort()

        uni = cherrypy.session.get(UNI_PARAM,None)
        if uni == None:
            if config.MODE == "regressiontest":
                uni = "foo"
            else:
                raise cherrypy.HTTPRedirect("/logout")
        try:
            d = es.to_python({'description' : description, 'instructor' : instructor})
            thisCourse = Course(description=d['description'],instructor=d['instructor'])

            # scan through user list to get users.  make sure they exist, then add to course
            lastUNI = None
            for thisUNI in uniList:
                # uniList is sorted, so all dupes would be consecutive.  only add once
                if thisUNI != lastUNI:
                    # don't add the student if he is the instructor of the course
                    if thisUNI != thisCourse.instructor.uni:
                        thisUser = Ecouser.select(Ecouser.q.uni == thisUNI)
                        # make sure this is a valid, existing user
                        if thisUser.count() == 1:
                            thisCourse.addEcouser(thisUser[0].id)
                            lastUNI = thisUNI

            print thisCourse.students

            cherrypy.session['message'] = "New course '" + description + "' has been created."
            raise cherrypy.HTTPRedirect("/course")
        except formencode.Invalid, e:
            defaults = {'description' : description, 'instructor' : instructor}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("create_course.pt",{'allInstructors' : [i for i in Ecouser.select()]}))
            output = parser.text()
            parser.close()
            return output

    @cherrypy.expose()
    def guest_login(self,uni="",password=""):
        return self.template("guest_login.pt",{})

    @cherrypy.expose()
    def add_guest_account_form(self):
        return self.template("add_guest_account.pt",{})

    @cherrypy.expose()
    def add_guest_account(self,uni="",firstname="",lastname="",password="",pass2=""):
        # TODO: this should be done with formencode
        if password != pass2:
            cherrypy.session['message'] = "Those passwords don't match"
            raise cherrypy.HTTPRedirect("/add_guest_account_form")
        if uni == "":
            cherrypy.session['message'] = "A user name is required"
            raise cherrypy.HTTPRedirect("/add_guest_account_form")
        u = Ecouser(uni=uni, password=password, firstname=firstname, lastname=lastname)
        cherrypy.session['message'] = "New user has been created.  Please log in"
        raise cherrypy.HTTPRedirect("/guest_login")


class RESTContent:
    @cherrypy.expose()
    def default(self, *vpath, **params):
        if len(vpath) == 1:
            identifier = vpath[0]
            action = self.show
        elif len(vpath) == 2:
            identifier, verb = vpath
            verb = verb.replace('.', '_')
            action = getattr(self, verb, None)
            if not action:
                raise cherrypy.NotFound
            if not action.exposed:
                raise cherrypy.NotFound
        else:
            raise cherrypy.NotFound
        items = self.query(identifier)
        if items.count() == 0:
            raise cherrypy.NotFound
        else:
            return action(items[0], **params)


class EcomapController(EcoControllerBase,RESTContent):
    _cpFilterList = [WindLoginFilter(after_login="/myList",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]
    @cherrypy.expose()
    def index(self):
        # this should really be a secured list of your ecomaps
        # it is a duplicate of the functionality of myList
        # it may be more appropriate to redirect to myList
        return self.template("list_ecomaps.pt",{'ecomaps' : [e for e in Ecomap.select()]})

    def query(self,id):
        return Ecomap.get(int(id))

    @cherrypy.expose()
    def edit_form(self,ecomap):
        defaults = {'name' : ecomap.name, 'description' : ecomap.description}
        parser = htmlfill.FillingParser(defaults)
        parser.feed(self.template("edit_ecomap.pt",{'ecomap' : ecomap}))
        output = parser.text()
        parser.close()
        return output

    @cherrypy.expose()
    def edit(self,ecomap,name="",description=""):
        es = EcomapSchema()
        try:
            d = es.to_python({'name' : name, 'description' : description, 'owner' : ecomap.ownerID})
            ecomap.name = d['name']
            ecomap.description = d['description']
            ecomap.modified = DateTime.now()
            cherrypy.session['message'] = "changes saved"
            raise cherrypy.HTTPRedirect("/ecomap/" + str(ecomap.id) + "/")

        except formencode.Invalid, e:
            defaults = {'name' : name, 'description' : description}
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
            parser.feed(self.template("edit_ecomap.pt",{'ecomap' : ecomap}))
            output = parser.text()
            parser.close()
            return output

    @cherrypy.expose()
    def show(self,ecomap,**kwargs):
        server = '/'.join(cherrypy.request.browserUrl.split('/')[:3])

        data = {
            'ecomap' : ecomap,
            'id' : ecomap.id,
            'ticket' : cherrypy.session.get(AUTH_TICKET_PARAM,None),
            'myName' : cherrypy.session.get('fullname',""),
            'server' : server,
            }
        return self.template("view_ecomap.pt",data)

    @cherrypy.expose()
    def delete(self,ecomap,confirm=""):
        if cherrypy.session.get(UNI_PARAM,None) in ADMIN_USERS:
            ecomap.destroySelf()
            cherrypy.session['message'] = "deleted"
        raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def flash(self,ecomap):
        flashData = {
            'id' : ecomap.id,
            'ticket' : cherrypy.session.get(AUTH_TICKET_PARAM,None),
            }
        return self.template("flash.pt",flashData)


class CourseController(EcoControllerBase,RESTContent):
    def query(self,id):
        return Course.get(int(id))

    @cherrypy.expose()
    def index(self):
        #import pdb; pdb.set_trace()
        # COURSE LIST
        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')

        if uni == None and config.MODE == "regressiontest":
            uni = "foo"

        if uni:
            myCourses = []
            # retreive the courses in which this user is a student
            thisUser = Ecouser.select(Ecouser.q.uni == uni)
            if thisUser.count() == 1:
                myCourses = thisUser[0].courses

            # retreive the course in which this user is an instructor
            instructorOf = Course.select(AND(Course.q.instructorID == Ecouser.q.id, Ecouser.q.uni == uni))
            if instructorOf.count() == 0:
                instructorOf = None

            if len(myCourses) == 1 and not instructorOf:
                # This is a student with only one course.  Redirect to that course
                raise cherrypy.HTTPRedirect("/course/%s/" % myCourses[0].id)
                
            if uni in ADMIN_USERS:
                allCourses = [e for e in Course.select(Course.q.instructorID == Ecouser.q.id, orderBy=['description'])]
            else:
                allCourses = None
            return self.template("list_courses.pt",{'loginName' : loginName, 'allCourses' : allCourses, 'myCourses' : myCourses, 'instructorOf' : instructorOf,})
        else:
            #No user logged in
            raise cherrypy.HTTPRedirect("/logout")

    @cherrypy.expose()
    def delete(self,course,confirm=""):
        #import pdb; pdb.set_trace()
        if cherrypy.session.get(UNI_PARAM,None) in ADMIN_USERS:

            # first remove the students from the course, then delete it
            students = course.students
            for student in students:
                course.removeEcouser(student.id)
            
            course.destroySelf()
            cherrypy.session['message'] = "deleted"
        raise cherrypy.HTTPRedirect("/course")
        
    @cherrypy.expose()
    def show(self,course,**kwargs):

        # This shows the list of ecomaps

        #import pdb; pdb.set_trace()

        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')
        postTo = "/course/%s/update" % course.id
        courseDescription = course.description

        if uni == None and config.MODE == "regressiontest":
            uni = "foo"

        if uni:
            # My ecomaps are the ecomaps I created in this course specifically
            myEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == uni, Ecomap.q.courseID == course.id), orderBy=['name'])]
            publicEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni != uni, Ecomap.q.courseID == course.id, Ecomap.q.public == True), orderBy=['name'])]
            
            if uni == course.instructor.uni:
                students = course.students
            else:
                students = None
            
            if uni in ADMIN_USERS:
                allEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecomap.q.courseID == course.id), orderBy=['name'])]
            else:
                allEcos = None
            for e in myEcos:
                e.createdStr = e.created.strftime("%m/%d/%Y")
                e.modifiedStr = e.modified.strftime("%m/%d/%Y")
            return self.template("list_ecomaps.pt",{'students' : students, 'loginName' : loginName, 'myEcomaps' : myEcos, 'publicEcomaps' : publicEcos, 'allEcomaps' : allEcos, 'postTo' : postTo, 'courseDescription' : courseDescription,})
        else:
            #No user logged in
            raise cherrypy.HTTPRedirect("/logout")

    @cherrypy.expose()
    def students(self,course):
        #import pdb; pdb.set_trace()
        postTo = "/course/%s/update_students" % course.id
        courseDescription = course.description
        return self.template("list_students.pt",{'students' : course.students, 'postTo' : postTo, 'courseDescription' : courseDescription,})

    @cherrypy.expose()
    def update_students(self,course,**kwargs):
        #import pdb; pdb.set_trace()
        action = kwargs['action']
        if action == 'Delete Selected':
            #check that some were selected
            studentList = kwargs.get('student_id',None)
            if studentList:
                if type(studentList) is str:
                    itemList = [int(kwargs['student_id'])]
                elif type(kwargs['student_id']) is list:
                    itemList = [k for k in kwargs['student_id']]
                else:
                    output = "error - unknown argument type"

                thisName = ""
                for item in itemList:
                    thisItem = Ecouser.get(item)
                    thisName += thisItem.firstname + " " + thisItem.lastname + ", "
                    course.removeEcouser(thisItem.id)
                cherrypy.session['message'] = "'" + thisName + "' has been deleted"
                raise cherrypy.HTTPRedirect("/course/%s/students" % course.id)

            else:
                raise cherrypy.HTTPRedirect("/course/%s/" % course.id)
        elif action == 'Add Student':
            studentUNI = kwargs.get('student_uni',None)
            if studentUNI:
                if studentUNI != course.instructor.uni:
                    thisUser = Ecouser.select(Ecouser.q.uni == studentUNI)
                    # make sure this is a valid, existing user
                    if thisUser.count() == 1:
                        course.addEcouser(thisUser[0].id)
                        cherrypy.session['message'] = "'" + thisUser[0].firstname + " " + thisUser[0].lastname + "' has been added"
                        raise cherrypy.HTTPRedirect("/course/%s/students" % course.id)
                    else:
                        print "not a valid user"
                        # not a valid user (we will be able to add these later and check with WIND
                else:
                    print "can't add instructor"
                    # can't add the instructor as a student

        # im only dealing with delete selected right now
        else:
            raise cherrypy.HTTPRedirect("/course/%s/" % course.id)

    @cherrypy.expose()
    def create_new(self):
        #import pdb; pdb.set_trace()
        
        uni = cherrypy.session.get(UNI_PARAM,None)
        if uni == None:
            if config.MODE == "regressiontest":
                uni = "foo"
            else:
                raise cherrypy.HTTPRedirect("/logout")

        d = {
            'name' : 'Enter Subject Name Here',
            'description' : 'Enter Description here',
            'owner' : Ecouser.select(Ecouser.q.uni == uni)[0].id,
            'course' : course.id
            }

        thisEcomap = Ecomap(name=d['name'],description=d['description'],owner=d['owner'],course=d['course'])
        raise cherrypy.HTTPRedirect("/ecomap/%s/" % thisEcomap.id)

    @cherrypy.expose()
    def update(self,course,**kwargs):
        #import pdb; pdb.set_trace()
        action = kwargs['action']
        #make sure at least one checkbox was selected
        ecomapList = kwargs.get('ecomap_id',None)
        redirectTo = "/course/%s/" % course.id
        
        if ecomapList:
            if type(ecomapList) is str:
                itemList = [int(kwargs['ecomap_id'])]
            elif type(kwargs['ecomap_id']) is list:
                itemList = [k for k in kwargs['ecomap_id']]
            else:
                output = "error - unknown argument type"
        else:
            raise cherrypy.HTTPRedirect(redirectTo)

        if action == 'Delete Selected':
            for item in itemList:
                thisItem = Ecomap.get(item)
                theDescription = thisItem.description
                thisItem.destroySelf()
            cherrypy.session['message'] = "'" + theDescription + "' has been deleted"
        elif action == 'share':
            es = EcomapSchema()
            for item in itemList:
                thisItem = Ecomap.get(item)
                thisItem.public = not thisItem.public
            cherrypy.session['message'] = "shared"

        raise cherrypy.HTTPRedirect(redirectTo)


