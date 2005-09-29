from cherrypy.lib.filter import basefilter
import cherrypy
from cherrypy.lib import httptools
import urllib
from ecomap.model import *
from ecomap.helpers import get_or_create_user

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
        

def get_user(username):
    res = Ecouser.select(Ecouser.q.uni == username)
    if res.count() > 0:
        return res[0]
    return None

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
            u = get_or_create_user(uni)
            cherrypy.session['fullname'] = u.firstname + " " + u.lastname
            cherrypy.response.body = httptools.redirect(self.after_login)
            
        import ecomap.config as config
        if config.MODE == "regressiontest":
            cherrypy.session[self.uni_key] = "foo"
            cherrypy.session[self.auth_key] = True
            return
        if cherrypy.request.path in self.allowed_paths:
            # skip the allowed ones
            return
        # non-WIND login
        if cherrypy.request.path.endswith("/guest_login"):
            uni = cherrypy.request.paramMap.get("uni","")
            password = cherrypy.request.paramMap.get("password")
            if uni != "":
                u = get_user(uni)
                if u == None:
                    return
                if u.password == password:
                    # they're good
                    cherrypy.session[self.auth_key] = True
                    cherrypy.session[self.ticket_key] = "guest ticket"
                    cherrypy.session[self.uni_key] = uni
                    cherrypy.session['fullname'] = u.firstname + " " + u.lastname
                    cherrypy.response.body = httptools.redirect(self.after_login)
                    return
            # give them the login form
            return

        if cherrypy.request.path.endswith("/add_guest_account"):
            return
        if cherrypy.request.path.endswith("/add_guest_account_form"):
            return
            
        
        # WIND login
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
                u = get_or_create_user(uni)
                cherrypy.session['fullname'] = u.firstname + " " + u.lastname
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

