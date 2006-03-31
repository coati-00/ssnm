from cherrypy.lib.filter import basefilter
import cherrypy
import urllib
from ecomap.model import *
from ecomap.helpers import get_or_create_user, get_user

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
        return (0,"The ticket was already used or was invalid.",[])
    else:
        return (0,"WIND did not return a valid response.",[])
        


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

    def backdoor(self):
        """ allow someone in through a special url for testing/debugging purposes"""
        u = get_or_create_user('kfe2102')        
        self.update_session(True,u.uni,[],"TICKET!!!",u.fullname())
        raise cherrypy.HTTPRedirect(self.after_login)

    def guest_login(self):
        """ allow someone without a uni to login """
        uni = cherrypy.request.paramMap.get("uni","")
        password = cherrypy.request.paramMap.get("password")
        if uni != "":
            u = get_user(uni)
            if u == None:
                cherrypy.session['message'] = "The user %s does not exist." % uni
                return
            if u.password == password:
                # they're good
                self.update_session(True,uni,[],"guest ticket",u.fullname())
                raise cherrypy.HTTPRedirect(self.after_login)
            else:
                cherrypy.session['message'] = "Login has failed."

        # give them the login form
        return        

    def wind_login(self):
        destination = urllib.quote(cherrypy.request.browserUrl)
        ticket_id = cherrypy.request.paramMap.get("ticketid","")
        if ticket_id == "":
            raise cherrypy.HTTPRedirect("%s?destination=%s&service=cnmtl_full_np" % (self.wind_url_base,destination))
        else:
            (success,uni,groups) = validate_wind_ticket(ticket_id)
            if int(success) == 0:
                cherrypy.response.body = ["The WIND authentication has failed. Please try again."]
                return
            u = get_or_create_user(uni)
            self.update_session(True,uni,groups,ticket_id,u.fullname())
            raise cherrypy.HTTPRedirect(self.after_login)

    def logout(self):
        self.update_session(False,"",[],"","")
        return
        
    def update_session(self,auth=False,uni="",groups=[],ticket="",fullname=""):
        cherrypy.session[self.auth_key] = auth
        cherrypy.session[self.uni_key] = uni
        cherrypy.session[self.groups_key] = groups
        cherrypy.session[self.ticket_key] = ticket
        cherrypy.session['fullname'] = fullname

    def beforeMain(self):
        if "/zerocool" in cherrypy.request.path:
            return self.backdoor()
            
        if cherrypy.config.get("TESTMODE",False):
            u = get_or_create_user("foo")
            self.update_session(True,"foo",[],"test ticket",u.fullname())
            return
        if cherrypy.request.path in self.allowed_paths:
            return

        # non-WIND login
        if cherrypy.request.path.endswith("/guest_login"):
            return self.guest_login()

        # WIND login
        if cherrypy.request.path.endswith(self.login_url):
            return self.wind_login()

        if cherrypy.request.path.endswith(self.logout_url):
            return self.logout()
        if cherrypy.session.get(self.auth_key,False):
            return
        else:
            raise cherrypy.HTTPRedirect(self.login_url)

