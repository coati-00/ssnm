import ecomap.model
import formencode
from formencode import validators
import cherrypy
from restclient import GET
from json import read as json_to_py

def safe_get_element_child(root,name):
    v = ""
    if root.getElementsByTagName(name)[0].hasChildNodes():
        v = root.getElementsByTagName(name)[0].firstChild.nodeValue
    return v


def createTables():
    ecomap.model.Ecouser.createTable(ifNotExists=True)
    ecomap.model.Course.createTable(ifNotExists=True)
    ecomap.model.Ecomap.createTable(ifNotExists=True)

def dropTables():
    ecomap.model.Ecomap.dropTable(ifExists=True)
    ecomap.model.Course.dropTable(ifExists=True)
    ecomap.model.Ecouser.dropTable(ifExists=True)

class EcomapSchema(formencode.Schema):
    name         = validators.String(not_empty=True)
    description  = validators.String()
    owner        = validators.Int()
    course       = validators.Int()

class EcouserSchema(formencode.Schema):
    uni          = validators.String(not_empty=True)
    securityLevel= validators.Int()
    firstname    = validators.String()
    lastname     = validators.String()

class CourseSchema(formencode.Schema):
    name         = validators.String(not_empty=True)
    description  = validators.String()
    instructor   = validators.Int()

def setup_for_tests():
    dropTables()
    createTables()

def teardown_tests():
    dropTables()

def ldap_lookup(username):
    r = json_to_py(GET("http://cdap.ccnmtl.columbia.edu/?uni=%s" % username))
    return (r['firstname'],r['lastname'])

def get_or_create_user(username,firstname="",lastname=""):
    """ if the user is already in the system, it returns the user object.
    otherwise, it creates a new one and returns that. the function has the
    side effect of putting the user into any class that wind says they
    should be a part of if they aren't already in it. """
    
    res = ecomap.model.Ecouser.select(ecomap.model.Ecouser.q.uni == username)
    u = None
    if res.count() > 0:
        # found the user. 
        u = res[0]
    else:
        #this user doesn't exist in our DB yet.  Get details from LDAP if possible
        (firstname,lastname) = ldap_lookup(username)
 	               
        if lastname == "":
            lastname = username
 	
        eus = EcouserSchema()
        d = eus.to_python({'uni' : username, 'securityLevel' : 2, 'firstname' : firstname, 'lastname' : lastname})
        u = ecomap.model.Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
    return u

def get_user_or_fail(username):
    res = ecomap.model.Ecouser.select(ecomap.model.Ecouser.q.uni == username)
    if res.count() > 0:
        return res[0]
    return None

def is_instructor(user,course):
    if not course.instructor == None:
        if course.instructor.uni == user.uni:
            return True
    return False
