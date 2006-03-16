from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL, site_root
from ecomap.helpers import EcomapSchema
import ecomap.config as config
from DisablePostParsingFilter import DisablePostParsingFilter

#from cherrypy.lib import httptools
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
#ADMIN_USERS = ("kfe2102","dm2150","ssw12")


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
                    if thisEcomap.public or thisEcomap.owner.uni == sessionUni or isAdmin(sessionUni):
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
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):
            defaults = {'name' : "", 'description' : "", 'instructor' : ""}
            parser = htmlfill.FillingParser(defaults)
            parser.feed(self.template("create_course.pt",{'allInstructors' : [i for i in Ecouser.select(orderBy=['firstname'])]}))
            parser.close()
            output = parser.text()
            return output
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def create_course(self,name="",description="",instructor="",students=""):
        #import pdb; pdb.set_trace()
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):

            es = CourseSchema()
    
            # MUST sanitize this comma delimited list
            uniList = students.split(",")
            
            # weed out dupes
            u = {}
            for x in uniList:
                u[x] = 1
            uniList = u.keys()
    
            invalidIDs = []
    
            uni = cherrypy.session.get(UNI_PARAM,None)
            try:
                d = es.to_python({'name' : name, 'description' : description, 'instructor' : instructor})
                thisCourse = Course(name=d['name'],description=d['description'],instructor=d['instructor'])
    
                # scan through user list to get users.  make sure they exist, then add to course
                if students != "":
                    for studentUNI in uniList:
                        # don't add the student if he is the instructor of the course
                        if studentUNI != thisCourse.instructor.uni:
                            thisUser = Ecouser.select(Ecouser.q.uni == studentUNI)
                            # make sure this is a valid, existing user
                            if thisUser.count() == 1:
                                if not thisUser[0] in thisCourse.students:
                                    thisCourse.addEcouser(thisUser[0].id)
                            else:
                                # add this user to our list of users
                                # make sure it is a valid UNI
                                (firstName,lastName) = ldap_lookup(studentUNI)
                                if firstName == "" and lastName == "":
                                    # not in the ldap.  bad uni.  exit
                                    invalidIDs.append(studentUNI)
                                else:
                                    eus = EcouserSchema()
                                    d = eus.to_python({'uni' : studentUNI, 'securityLevel' : 2, 'firstname' : firstName, 'lastname' : lastName})
                                    thisUser = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
                                    if not thisUser in thisCourse.students:
                                        thisCourse.addEcouser(thisUser.id)
                    print thisCourse.students
   
                cherrypy.session['message'] = "New course '" + name + "' has been created"
                if len(invalidIDs) > 0:
                    cherrypy.session['message'] += " but the following UNIs were not valid: %s" % invalidIDs
                raise cherrypy.HTTPRedirect("/course")
            except formencode.Invalid, e:
                defaults = {'name' : name, 'description' : description, 'instructor' : instructor}
                parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
                parser.feed(self.template("create_course.pt",{'allInstructors' : [i for i in Ecouser.select()]}))
                parser.close()
                output = parser.text()
                return output
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")


    @cherrypy.expose()
    def guest_login(self,uni="",password=""):
        return self.template("guest_login.pt",{})

    @cherrypy.expose()
    def add_guest_account_form(self):
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):
            return self.template("add_guest_account.pt",{})
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def add_guest_account(self,uni="",firstname="",lastname="",password="",pass2=""):
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):
            # TODO: this should be done with formencode
            if password != pass2:
                cherrypy.session['message'] = "Those passwords don't match"
                raise cherrypy.HTTPRedirect("/add_guest_account_form")
            if uni == "":
                cherrypy.session['message'] = "A user name is required"
                raise cherrypy.HTTPRedirect("/add_guest_account_form")
            u = Ecouser(uni=uni, securityLevel=2, password=password, firstname=firstname, lastname=lastname)
            cherrypy.session['message'] = "New user has been created.  Please log in"
            raise cherrypy.HTTPRedirect("/guest_login")
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def admin_users_form(self):
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):
            loginName = cherrypy.session.get('fullname', 'unknown')
            return self.template("admin_users.pt",{'loginName' : loginName, 'allUsers' : [i for i in Ecouser.select(orderBy=['securityLevel','firstname'])]})
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")
        
    @cherrypy.expose()
    def admin_users(self,**kwargs):
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):
            itemList = kwargs.get('user_id',None)
            action = kwargs['action']
            if itemList:
                if type(itemList) is str:
                    personList = [int(kwargs['user_id'])]
                elif type(kwargs['user_id']) is list:
                    personList = [k for k in kwargs['user_id']]
                else:
                    output = "error - unknown argument type"

            thisName = ""
            if action == 'Delete Selected':
                for person in personList:
                    # get the user, remove him from all his courses and delete him
                    thisPerson = Ecouser.get(person)
                    thisName += thisPerson.firstname + " " + thisPerson.lastname + ", "
                    hisCourses = thisPerson.courses
                    for thisCourse in hisCourses:
                        thisCourse.removeEcouser(thisPerson.id)
                    thisPerson.destroySelf()
                cherrypy.session['message'] = "'" + thisName + "' has been deleted"
                raise cherrypy.HTTPRedirect("/admin_users_form")

            if action == 'Toggle Admin':
                #import pdb; pdb.set_trace()
                for person in personList:
                    # get the user and toggle his admin status
                    thisPerson = Ecouser.get(person)
                    if thisPerson.securityLevel == 2:
                        thisPerson.securityLevel = 1
                    elif thisPerson.securityLevel == 1:
                        thisPerson.securityLevel = 2
                cherrypy.session['message'] = "Users have had their status changed"
                raise cherrypy.HTTPRedirect("/admin_users_form")

            elif action == 'Add User':
                 userUNI = kwargs.get('user_uni',None)
                 if userUNI:
                     (firstName,lastName) = ldap_lookup(userUNI)
                     if firstName == "" and lastName == "":
                         # not in the ldap.  bad uni.  exit
                         cherrypy.session['message'] = "Sorry, That is not a valid UNI"
                     else:
                         eus = EcouserSchema()
                         d = eus.to_python({'uni' : userUNI, 'securityLevel' : 2, 'firstname' : firstName, 'lastname' : lastName})
                         thisUser = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
                         cherrypy.session['message'] = "'" + d['firstname'] + " " + d['lastname'] + "' has been added"
                 raise cherrypy.HTTPRedirect("/admin_users_form")
            
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")
        

class RESTContent:
    @cherrypy.expose()
    def default(self, *vpath, **params):
        #import pdb; pdb.set_trace()
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
        item = self.query(identifier)
        if item == None:
            raise cherrypy.NotFound
        else:
            return action(item, **params)


class EcomapController(EcoControllerBase,RESTContent):
    _cpFilterList = [WindLoginFilter(after_login="/course",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]

    # convenience redirect to the RIGHT place
    @cherrypy.expose()
    def index(self):
        raise cherrypy.HTTPRedirect("/course")

    def query(self,id):
        return Ecomap.get(int(id))

    @cherrypy.expose()
    def show(self,ecomap,**kwargs):
        #import pdb; pdb.set_trace()
        server = '/'.join(cherrypy.request.browserUrl.split('/')[:3]) + '/'

        data = {
            'ecomap' : ecomap,
            'id' : ecomap.id,
            'ticket' : cherrypy.session.get(AUTH_TICKET_PARAM,None),
            'myName' : cherrypy.session.get('fullname',""),
            'server' : server,
            }
        return self.template("view_ecomap.pt",data)


def action_auth(f):
    """ control over who can do what """
    def wrapped(*args, **kwargs):
        import pdb; pdb.set_trace()
        if config.MODE == "regressiontest":
            return f(*args,**kwargs)
        uni = cherrypy.session.get(UNI_PARAM, None)
  #      if uni:
  #          
  #          authUsers = kwargs['authorized'].split(",")
            
        

        # NOW, since you are logged in ok, check if you're allowed to do what you're trying to do
        
#       userid        = get_cookie("quip_username")
#       authenticated = get_cookie('quip_authenticated')
#       if authenticated != "1":
#           raise cherrypy.HTTPRedirect("/login")
#       else:
        return f(*args,**kwargs)
    return wrapped

class CourseController(EcoControllerBase,RESTContent):
    def query(self,id):
        return Course.get(int(id))

    @cherrypy.expose()
    def index(self):
        #import pdb; pdb.set_trace()
        # COURSE LIST
        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')


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
                
            if isAdmin(uni):
                allCourses = [e for e in Course.select(Course.q.instructorID == Ecouser.q.id, orderBy=['name'])]
            else:
                allCourses = None
            return self.template("list_courses.pt",{'loginName' : loginName, 'allCourses' : allCourses, 'myCourses' : myCourses, 'instructorOf' : instructorOf})
        else:
            #No user logged in
            raise cherrypy.HTTPRedirect("/logout")

    @cherrypy.expose()
    def delete(self,course,confirm=""):
        #import pdb; pdb.set_trace()
        if isAdmin(cherrypy.session.get(UNI_PARAM,None)):

            # first remove the students from the course, then delete it
            students = course.students
            for student in students:
                course.removeEcouser(student.id)
            
            course.destroySelf()
            cherrypy.session['message'] = "deleted"
            raise cherrypy.HTTPRedirect("/course")
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")
        
    @cherrypy.expose()
    def show(self,course,**kwargs):
        # This shows the list of ecomaps
        #import pdb; pdb.set_trace()

        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')
        courseName = course.name

        if uni:
            # My ecomaps are the ecomaps I created in this course specifically
            myEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == uni, Ecomap.q.courseID == course.id), orderBy=['name'])]
            publicEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni != uni, Ecomap.q.courseID == course.id, Ecomap.q.public == True), orderBy=['name'])]
            
            if isAdmin(uni) or isInstructor(uni,course):
                allEcos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecomap.q.courseID == course.id), orderBy=['name'])]
            else:
                allEcos = None
            for e in myEcos:
                e.createdStr = e.created.strftime("%m/%d/%Y")
                e.modifiedStr = e.modified.strftime("%m/%d/%Y")
            return self.template("list_ecomaps.pt",{'loginName' : loginName, 'myEcomaps' : myEcos, 'publicEcomaps' : publicEcos, 'allEcomaps' : allEcos, 'courseName' : courseName,})
        else:
            #No user logged in
            raise cherrypy.HTTPRedirect("/logout")


    @cherrypy.expose()
    def edit_form(self,course):
        #import pdb; pdb.set_trace()
        uni = cherrypy.session.get(UNI_PARAM, None)
        if isAdmin(uni) or isInstructor(uni,course):

            defaults = {'name' : course.name, 'description' : course.description, 'instructor' : course.instructor.id}
            parser = htmlfill.FillingParser(defaults)
            parser.feed(self.template("edit_course.pt",{'isAdmin': isAdmin(uni), 'courseName' : course.name, 'course' : course, 'allInstructors' : [i for i in Ecouser.select(orderBy=['firstname'])]}))
            parser.close()
            output = parser.text()
            return output
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def edit(self,course,name="",description="",instructor=""):
        uni = cherrypy.session.get(UNI_PARAM, None)
        if isAdmin(uni) or isInstructor(uni,course):

            es = CourseSchema()
    
            try:
                d = es.to_python({'name' : name, 'description' : description, 'instructor' : instructor})
                course.name = d['name']
                course.description = d['description']
                course.instructor = d['instructor']
                cherrypy.session['message'] = "changes saved"
                raise cherrypy.HTTPRedirect("/course/" + str(course.id) + "/")
    
            except formencode.Invalid, e:
                defaults = {'name' : course.name, 'description' : course.description, 'instructor' : course.instructor.id}
                parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
                parser.feed(self.template("edit_course.pt",{'isAdmin': isAdmin(uni), 'courseName' : course.name, 'course' : course, 'allInstructors' : [i for i in Ecouser.select(orderBy=['firstname'])]}))
                parser.close()
                output = parser.text()
                return output
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def students(self,course):
        uni = cherrypy.session.get(UNI_PARAM, None)
        loginName = cherrypy.session.get('fullname', 'unknown')
        if isAdmin(uni) or isInstructor(uni,course):
            #import pdb; pdb.set_trace()
            courseName = course.name
            return self.template("list_students.pt",{'loginName' : loginName, 'students' : course.students, 'courseName' : courseName,})
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")


    @cherrypy.expose()
    def update_students(self,course,**kwargs):
        #import pdb; pdb.set_trace()
        uni = cherrypy.session.get(UNI_PARAM, None)
        if isAdmin(uni) or isInstructor(uni,course):
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
                            if not thisUser[0] in course.students:
                                course.addEcouser(thisUser[0].id)
                                cherrypy.session['message'] = "'" + thisUser[0].firstname + " " + thisUser[0].lastname + "' has been added"
                        else:
                            # add this user to our list of users
                            # make sure it is a valid UNI
                            (firstName,lastName) = ldap_lookup(studentUNI)
                            if firstName == "" and lastName == "":
                                # not in the ldap.  bad uni.  exit
                                cherrypy.session['message'] = "Sorry, That is not a valid UNI"
                            else:
                                eus = EcouserSchema()
                                d = eus.to_python({'uni' : studentUNI, 'securityLevel' : 2, 'firstname' : firstName, 'lastname' : lastName})
                                thisUser = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
                                if not thisUser in course.students:
                                    course.addEcouser(thisUser.id)
                                    cherrypy.session['message'] = "'" + d['firstname'] + " " + d['lastname'] + "' has been added"
                    else:
                        cherrypy.session['message'] = "Sorry, The instructor cannot be a student in the class"
                        # can't add the instructor as a student
                    raise cherrypy.HTTPRedirect("/course/%s/students" % course.id)
    
            else:
                raise cherrypy.HTTPRedirect("/course/%s/" % course.id)      
        else:
            cherrypy.session['message'] = "You do not have authorization to perform that action.  This event will be reported"
            raise cherrypy.HTTPRedirect("/course")


    @cherrypy.expose()
    def create_new(self,course):
        #import pdb; pdb.set_trace()
        
        uni = cherrypy.session.get(UNI_PARAM,None)

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
            # TODO:
            # if you are the owner or you're the instructor or an admin

            # weed out dupes
            u = {}
            for x in itemList:
                u[x] = 1
            itemList = u.keys()

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


