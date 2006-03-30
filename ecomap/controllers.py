import turbogears, cherrypy, urllib
from turbogears import controllers

from ecomap.model import *
from ecomap.helpers import *
from ecomap.helpers.cherrytal import CherryTAL, site_root
from ecomap.helpers import EcomapSchema
from DisablePostParsingFilter import DisablePostParsingFilter

#from cherrypy.lib import httptools
from mx import DateTime
import sys, os.path
import StringIO
import cgitb
import formencode
from formencode import validators
from formencode import htmlfill
from xml.dom.minidom import parseString

UNI_PARAM = "UNI"
AUTH_TICKET_PARAM = "auth_ticket"
#ADMIN_USERS = ("kfe2102","dm2150","ssw12")

def get_user():
    return cherrypy.session.get("UNI",None)

def get_auth():
    return cherrypy.session.get("auth_ticket",None)

def get_fullname():
    return cherrypy.session.get('fullname','')

def message(m):
    cherrypy.session['message'] = m

def build_controllers():
    cherrypy.root             = Eco()
    cherrypy.root.ecomap      = EcomapController()
    cherrypy.root.course      = CourseController()

class EcoControllerBase(CherryTAL):
    _template_dir = "ecomap/templates"
    _globals = {'login_name' : lambda: get_fullname()}

    def referer(self):
        return cherrypy.request.headerMap.get('Referer','/')

    def _cpOnError(self):
        err = sys.exc_info()
        if cherrypy.config.get('DEBUG',False):
            sio = StringIO.StringIO()
            hook = cgitb.Hook(file=sio)
            hook.handle(info=err)
            cherrypy.response.headerMap['Content-Type'] = 'text/html'
            cherrypy.response.body = [sio.getvalue()]
        else:
            # Do something else here.
            cherrypy.response.body = ['Error: ' + str(err[0])]

from WindLoginFilter import WindLoginFilter

def ensure_list(self,potential_list):
    if type(potential_list) is str:
        return [int(potential_list)]
    elif type(potential_list) is list:
        return potential_list
    else:
        return []


def admin_only(f):
    def wrapped(*args,**kwargs):
        if is_admin(get_user()):
            return f(*args,**kwargs)
        else:
            message("You are not authorized to perform that action.  This event will be reported.")            
            raise cherrypy.HTTPRedirect("/course/")
    return wrapped

class Eco(EcoControllerBase):
    # enable filtering to disable post filtering on the postTester funcion
    _cpFilterList = [ DisablePostParsingFilter(),
                      WindLoginFilter(after_login="/course",allowed_paths=["/","/flashConduit"],
                                      uni_key=UNI_PARAM,ticket_key=AUTH_TICKET_PARAM)]

    @cherrypy.expose()
    def index(self):
        return self.template("index.pt",{})

    @cherrypy.expose()
    def about(self):
        return self.template("about.pt",{})

    @cherrypy.expose()
    def help(self):
        return self.template("help.pt",{})

    @cherrypy.expose()
    def contact(self):
        return self.template("contact.pt",{})


    #legacy redirect for flash
    @cherrypy.expose()
    def myList(self):
        raise cherrypy.HTTPRedirect("/course")

    @cherrypy.expose()
    def flashConduit(self,HTMLid="",HTMLticket=""):
        #import pdb; pdb.set_trace()

        #First, check to make sure there's a session established
        session_uni = get_user()
        session_ticket = get_auth()

        if not session_uni and session_ticket:
            response_data = "<response>Session error</response>"

        else:

            post_length = int(cherrypy.request.headerMap.get('Content-Length',0))
            post_data = cherrypy.request.rfile.read(post_length)

            #post_data is going to have a ticket and an id to parse out

            try:
                doc = parseString(post_data)
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
            data_node = root.getElementsByTagName("flashData")[0].toxml()

            if ticketid == session_ticket:
                #tickets match, so the session is valid
                if not ecoid == "":
                    this_ecomap = Ecomap.get(ecoid)
                    # if this is public or it's yours or Susan, Debbie or I am logged in, allow the data to Flash
                    if this_ecomap.public or this_ecomap.owner.uni == session_uni or is_admin(session_uni):
                        if action == "load":
                            if this_ecomap.owner.uni == session_uni:
                                response_data = "<data><response>OK</response><isreadonly>false</isreadonly><name>" + this_ecomap.name + "</name><description>" + this_ecomap.description + "</description>" + this_ecomap.flashData + "</data>"
                            else:
                                #send it in as read only
                                response_data = "<data><response>OK</response><isreadonly>true</isreadonly><name>" + this_ecomap.name + "</name><description>" + this_ecomap.description + "</description>" + this_ecomap.flashData + "</data>"
                        elif action == "save":
                            #if this is your ecomap, you can save it, otherwise, youre out of luck
                            if this_ecomap.owner.uni == session_uni:
                                if root.getElementsByTagName("name")[0].hasChildNodes():
                                    ecoName = root.getElementsByTagName("name")[0].firstChild.nodeValue
                                else:
                                    ecoName = ""
                                if root.getElementsByTagName("description")[0].hasChildNodes():
                                    ecoDescription = root.getElementsByTagName("description")[0].firstChild.nodeValue
                                else:
                                    ecoDescription = ""
                                this_ecomap.flashData = data_node
                                this_ecomap.name = ecoName
                                this_ecomap.description = ecoDescription
                                this_ecomap.modified = DateTime.now()
                                #want to check if this actually saves so i can REALLY return an OK
                                #if it doesn't save, return NOT OK
                                response_data = "<data><response>OK</response></data>"
                            else:
                                response_data = "<data><response>This is not your social support network map.</response></data>"
                        else:
                            print "unknown data action"
                            response_data = "<data><response>Unknown data action</response></data>"
                        print this_ecomap.description
                    else:
                        response_data = "<data><response>This is not your social support network map. Also, it isn't public.</response></data>"
                        print "not your ecomap and not public"
                else:
                    response_data = "<data><response>That social support network map ID does'nt exist.</response></data>"
                    print "not a valid ecomap id"
            else:
                response_data = "<data><response>Your session may have timed out.</response></data>"
                print "This in't a valid session you little hacker! ;)"


        return response_data

    @cherrypy.expose()
    def logout(self,**kwargs):
        return self.template("logout.pt",{})

    def course_form(self,name,description,instructor,e=None):
        uni = get_user()
        defaults = {'name' : name, 'description' : description, 'instructor' : instructor}
        if e == None:
            parser = htmlfill.FillingParser(defaults)
        else:
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
        parser.feed(self.template("create_course.pt",{'all_instructors' : list(Ecouser.select(orderBy=['firstname']))}))
        parser.close()
        return parser.text()


    @cherrypy.expose()
    @admin_only
    def create_course_form(self):
        return self.course_form("","","")

    @cherrypy.expose()
    @admin_only
    def create_course(self,name="",description="",instructor="",students=""):
        es = CourseSchema()

        # MUST sanitize this comma delimited list
        uni_list = students.split(",")

        # weed out dupes
        u = {}
        for x in uni_list:
            u[x] = 1
        uni_list = u.keys()

        try:
            d = es.to_python({'name' : name, 'description' : description, 'instructor' : instructor})
            this_course = Course(name=d['name'],description=d['description'],instructor=d['instructor'])
            invalid_ids = this_course.add_students(uni_list)

            m = "The new course '" + name + "' has been created."
            if len(invalid_ids) > 0:
                m += " but the following UNIs were not valid: %s" % invalid_ids
            message(m)
            raise cherrypy.HTTPRedirect("/course")
        except formencode.Invalid, e:
            return self.course_form(name,description,instructor,e)

    @cherrypy.expose()
    def guest_login(self,uni="",password=""):
        return self.template("guest_login.pt",{})

    @cherrypy.expose()
    @admin_only
    def add_guest_account_form(self):
        return self.template("add_guest_account.pt",{})

    @cherrypy.expose()
    @admin_only
    def add_guest_account(self,uni="",firstname="",lastname="",password="",pass2=""):
        # TODO: this should be done with formencode
        if password != pass2:
            message("Those passwords don't match")
            raise cherrypy.HTTPRedirect("/add_guest_account_form")
        if uni == "":
            message("A user name is required")
            raise cherrypy.HTTPRedirect("/add_guest_account_form")
        u = Ecouser(uni=uni, securityLevel=2, password=password, firstname=firstname, lastname=lastname)
        message("New user has been created.  Please log in")
        raise cherrypy.HTTPRedirect("/guest_login")

    @cherrypy.expose()
    @admin_only
    def admin_users_form(self):
        return self.template("admin_users.pt",{'allUsers' : list(Ecouser.select(orderBy=['securityLevel','firstname']))})

    def delete_users(self,users):
        names = []
        for id in users:
            # get the user, remove him from all his courses and delete him
            user = Ecouser.get(id)
            names.append(user.fullname())
            user.delete()
        message("'" + ', '.join(names) + "' has been deleted.")
        raise cherrypy.HTTPRedirect("/admin_users_form")

    def toggle_admin(self,users):
        for id in users:
            # get the user and toggle his admin status
            user = Ecouser.get(id)
            user.toggle_admin()

        message("Users have had their status changed.")
        raise cherrypy.HTTPRedirect("/admin_users_form")
        

    def add_user(self,uni):
        if uni == "":
            return
        (firstname,lastname) = ldap_lookup(uni)
        if firstname == "" and lastname == "":
            # not in the ldap.  bad uni.  exit
            message("That is not a valid UNI.")
        else:
            eus = EcouserSchema()
            d = eus.to_python({'uni' : uni, 'securityLevel' : 2, 'firstname' : firstname, 'lastname' : lastname})
            this_user = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
            message("'" + d['firstname'] + " " + d['lastname'] + "' has been added")


    @cherrypy.expose()
    @admin_only
    def admin_users(self,**kwargs):
        person_list = ensure_list(kwargs.get('user_id',None))
        action = kwargs['action']

        if action == 'Delete':
            return self.delete_users(person_list)
        
        if action == 'Change Security Level':
            return self.toggle_admin(person_list)

        elif action == 'Add User':
            self.add_user(kwargs.get('user_uni',None))
            raise cherrypy.HTTPRedirect("/admin_users_form")
        elif action == 'Add Guest Account':
            raise cherrypy.HTTPRedirect("/add_guest_account_form")
        

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
            'ecomap'     : ecomap,
            'id'         : ecomap.id,
            'ticket'     : get_auth(),
            'myName'     : get_fullname(),
            'server'     : server,
            'returnPath' : "course/%s" % ecomap.course.id,
            }
        return self.template("view_ecomap.pt",data)


def restrict_to_instructor_or_admin(f):
    def decorator(self,course,*args,**kwargs):
        if admin_or_instructor(get_user(),course):
            return f(self,course,*args,**kwargs)
        else:
            message("You don't have authorization to perform that action.  This event will be reported.")
            raise cherrypy.HTTPRedirect("/course")
    return decorator

def admin_or_instructor(uni,course):
    return is_admin(uni) or is_instructor(uni,course)

class CourseController(EcoControllerBase,RESTContent):
    def query(self,id):
        return Course.get(int(id))

    @cherrypy.expose()
    def index(self):
        """ course list """
        # retreive the courses in which this user is a student
        user = Ecouser.select(Ecouser.q.uni == get_user())[0]
        my_courses = user.courses

        # retreive the course in which this user is an instructor
        instructor_of = user.instructor_courses()
        if instructor_of.count() == 0:
            instructor_of = None

        if len(my_courses) == 1 and not instructor_of:
            # This is a student with only one course.  Redirect to that course
            raise cherrypy.HTTPRedirect("/course/%s/" % my_courses[0].id)

        all_courses = []
        if is_admin(get_user()):
            all_courses = get_all_courses()

        return self.template("list_courses.pt",{'all_courses' : all_courses, 'my_courses' : my_courses, 'instructor_of' : instructor_of})

    @cherrypy.expose()
    @admin_only
    def delete(self,course,confirm=""):
        course.delete()
        message("deleted")
        raise cherrypy.HTTPRedirect("/course")
        
    @cherrypy.expose()
    def show(self,course,**kwargs):
        # This shows the list of ecomaps
        uni = get_user()
        course_name = course.name

        # My ecomaps are the ecomaps I created in this course specifically
        my_ecos = list(Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni == uni, Ecomap.q.courseID == course.id), orderBy=['name']))
        public_ecos = list(Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecouser.q.uni != uni, Ecomap.q.courseID == course.id, Ecomap.q.public == True), orderBy=['name']))

        if uni == course.instructor.uni:
            students = course.students
        else:
            students = None

        if admin_or_instructor(uni,course):
            all_ecos = [e for e in Ecomap.select(AND(Ecomap.q.ownerID == Ecouser.q.id, Ecomap.q.courseID == course.id), orderBy=['name'])]
        else:
            all_ecos = None
        return self.template("list_ecomaps.pt",{'my_ecomaps' : my_ecos, 'public_ecomaps' : public_ecos, 'all_ecomaps' : all_ecos, 'course_name' : course_name,})


    def course_form(self,course, e=None):
        defaults = {'name' : course.name, 'description' : course.description, 'instructor' : course.instructor.id}
        if e != None:
            parser = htmlfill.FillingParser(defaults,errors=e.unpack_errors())
        else:
            parser = htmlfill.FillingParser(defaults)        
        parser.feed(self.template("edit_course.pt",{'is_admin': is_admin(get_user()),
                                                    'course_name' : course.name, 'course' : course,
                                                    'all_instructors' : [i for i in Ecouser.select(orderBy=['firstname'])]}))
        parser.close()
        return parser.text()


    @cherrypy.expose()
    @admin_only
    def edit_form(self,course):
        return self.course_form(course)

    @cherrypy.expose()
    @admin_only
    def edit(self,course,name="",description="",instructor=""):
        uni = get_user()
        es = CourseSchema()

        try:
            d = es.to_python({'name' : name, 'description' : description, 'instructor' : instructor})
            course.name = d['name']
            course.description = d['description']
            course.instructor = d['instructor']
            message("changes saved")
            raise cherrypy.HTTPRedirect("/course/" + str(course.id) + "/")

        except formencode.Invalid, e:
            return self.course_form(course,e)


    @cherrypy.expose()
    @restrict_to_instructor_or_admin
    def students(self,course):
        uni = get_user()
        course_name = course.name
        return self.template("list_students.pt",{'students' : course.students, 'course_name' : course_name,})



    @cherrypy.expose()
    @restrict_to_instructor_or_admin
    def update_students(self,course,**kwargs):
        uni = get_user()
        action = kwargs['action']
        if action == 'Delete Selected':
            #check that some were selected
            student_list = ensure_list(kwargs.get('student_id',None))
            if student_list:
                this_name = ""
                for item in item_list:
                    this_item = Ecouser.get(item)
                    this_name += this_item.firstname + " " + this_item.lastname + ", "
                    course.removeEcouser(this_item.id)
                message("'" + this_name + "' has been deleted.")
                raise cherrypy.HTTPRedirect("/course/%s/students" % course.id)
            else:
                return "error - unknown argument type"
        else:
            raise cherrypy.HTTPRedirect("/course/%s/" % course.id)      

    @cherrypy.expose()
    def create_new(self,course):
        uni = get_user()

        d = {
            'name'        : 'Enter Subject Name Here',
            'description' : 'Enter Description here',
            'owner'       : Ecouser.select(Ecouser.q.uni == uni)[0].id,
            'course'      : course.id
            }

        this_ecomap = Ecomap(name=d['name'],description=d['description'],owner=d['owner'],course=d['course'])
        raise cherrypy.HTTPRedirect("/ecomap/%s/" % this_ecomap.id)

    @cherrypy.expose()
    def update(self,course,**kwargs):
        action = kwargs['action']
        item_list = [Ecomap.get(id) for id in ensure_list(kwargs.get('ecomap_id',None))]

        if action == 'Delete Selected':
            # TODO:
            # if you are the owner or you're the instructor or an admin

            # weed out dupes
            u = {}
            for x in item_list:
                u[x.id] = x
            item_list = u.values()
            self.delete_ecomaps(item_list)
            
        elif action == 'share':
            for item in item_list:
                item.public = not item.public
            message("shared")

        raise cherrypy.HTTPRedirect("/course/%s/" % course.id)

    def delete_ecomaps(self,ecomaps):
        for ecomap in ecomaps:
            description = ecomap.description
            ecomap.destroySelf()
            message("'" + description + "' has been deleted.")
