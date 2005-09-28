from cherrypy.lib.filter import basefilter
import cherrypy
from cherrypy.lib import httptools
import urllib
from ecomap.model import *

def validate_wind_ticket(ticketid):
    """
    checks a wind ticketid.
    if successful, it returns (1,username)
    otherwise it returns (0,error message)
    """
    
    if ticketid == "":
        return (0,'no ticketid')
    uri = "https://wind.columbia.edu/validate?ticketid=%s" % ticketid
    import urllib
    response = urllib.urlopen(uri).read()
    lines = response.split("\n")
    if lines[0] == "yes":
        username = lines[1]
        groups = [line for line in lines[1:] if line != ""]
        return (1,username,groups)
    elif lines[0] == "no":
        return (0,"the ticket was already used or was invalid",[])
    else:
        return (0,"WIND did not return a valid response",[])
        
#This function needs to be linked to the data model
#LDAP lookup section can be used as is ** :)
def get_or_create_user(username,firstname="",lastname=""):

    """ if the user is already in the system, it returns the user object.
    otherwise, it creates a new one and returns that. the function has the
    side effect of putting the user into any class that wind says they
    should be a part of if they aren't already in it. """

    from ecomap.helpers import *
    res = Ecouser.select(Ecouser.q.uni == username)

    if res.count() > 0:
        # found the user. 
        u = res[0]
        cherrypy.session['fullname'] = u.firstname + " " + u.lastname
        return u
    
    else:
        #this user doesn't exist in our DB yet.  Get details from LDAP if possible
        try:
            import ldap
            LDAP_SERVER = "ldap.columbia.edu"
            BASE_DN = "o=Columbia University, c=us"
            l = ldap.open(LDAP_SERVER)
            baseDN = BASE_DN
            searchScope = ldap.SCOPE_SUBTREE
            retrieveAttributes = None
            searchFilter = "uni=*%s" % username
            ldap_result_id = l.search(baseDN, searchScope, searchFilter,
                    retrieveAttributes)
            result_set = []
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if result_data == []:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        values = result_data[0][1]
                        for k, v in values.items():
                            if k == 'sn':
                                lastname = v[0]
                            if k == 'givenname':
                                firstname = v[0]
        except ImportError:
            # no ldap library
            pass
                
        if lastname == "":
            lastname = username

        cherrypy.session['fullname'] = firstname + " " + lastname

        eus = EcouserSchema()
        d = eus.to_python({'uni' : username, 'firstname' : firstname, 'lastname' : lastname})
        u = Ecouser(uni=d['uni'],firstname=d['firstname'],lastname=d['lastname'])

        return u
        

class WindLoginFilter(basefilter.BaseFilter):
    def __init__(self,after_login="/", login_url = "/login", logout_url = "/logout", allowed_paths=[],
                 uni_key = "uni", ticket_key = "ticket_id", auth_key = "authenticated", groups_key = "groups",
                 wind_url_base = "https://wind.columbia.edu/login",
                 ):
        self.allowed_paths = allowed_paths
        self.after_login   = after_login
        self.login_url     = login_url
        self.logout_url    = logout_url
        self.uni_key       = uni_key
        self.ticket_key    = ticket_key
        self.auth_key      = auth_key
        self.groups_key    = groups_key
        self.wind_url_base = wind_url_base
    
    def beforeMain(self):
        if "/css/" in cherrypy.request.path:
            return
        if "/images/" in cherrypy.request.path:
            return
        if "/flash/" in cherrypy.request.path:
            return
        if "/favicon.ico" in cherrypy.request.path:
            return
        if "/zerocool" in cherrypy.request.path:
            uni = 'kfe2102'
            ticket_id = "TICKET!!!"
            cherrypy.session[self.uni_key] = uni
            cherrypy.session[self.auth_key] = True
            cherrypy.session[self.ticket_key] = ticket_id
            get_or_create_user(uni)
            cherrypy.response.body = httptools.redirect(self.after_login)
            
        import ecomap.config as config
        if config.MODE == "regressiontest":
            cherrypy.session[self.uni_key] = "foo"
            cherrypy.session[self.auth_key] = True
            return
        if cherrypy.request.path in self.allowed_paths:
            # skip the allowed ones
            return
        if cherrypy.request.path.endswith(self.login_url):
            destination = urllib.quote(cherrypy.request.browserUrl)
            ticket_id = cherrypy.request.paramMap.get("ticketid","")
            if ticket_id == "":
                cherrypy.response.body = httptools.redirect("%s?destination=%s&service=cnmtl_full_np" % (self.wind_url_base,destination))
                return
            else:
                (success,uni,groups) = validate_wind_ticket(ticket_id)
                if int(success) == 0:
                    cherrypy.response.body = ["WIND authentication failed. please try again or report this as a bug."]
                    return

                cherrypy.session[self.auth_key] = True
                cherrypy.session[self.ticket_key] = ticket_id
                cherrypy.session[self.uni_key] = uni
                cherrypy.session[self.groups_key] = groups
                get_or_create_user(uni)
                cherrypy.response.body = httptools.redirect(self.after_login)

        if cherrypy.request.path.endswith(self.logout_url):
            cherrypy.session[self.auth_key] = False
            cherrypy.session[self.uni_key] = ""
            cherrypy.session[self.groups_key] = []
            cherrypy.session[self.ticket_key] = ""

            #cherrypy.response.body = ["You are now logged out."]
            return

        if cherrypy.session.get(self.auth_key,False):
            return
        else:
            cherrypy.response.body = httptools.redirect(self.login_url)

