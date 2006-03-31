from cherrypy.lib.filter import basefilter
import cherrypy
import urllib

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
    def __init__(self,update_session_callback,get_user,testmode,is_authenticated,is_testmode,after_login="/", login_url = "/login",
                 logout_url = "/logout", allowed_paths=[],strict_allowed_paths=[],
                 auth_key = "authenticated", wind_url_base = "https://wind.columbia.edu/login",
                 special_paths = {}):
        self.update_session = update_session_callback
        self.get_user      = get_user
        self.testmode      = testmode
        self.is_authenticated = is_authenticated
        self.is_testmode = is_testmode
        self.allowed_paths = allowed_paths
        self.strict_allowed_paths = strict_allowed_paths
        self.after_login   = after_login
        self.login_url     = login_url
        self.logout_url    = logout_url
        self.auth_key      = auth_key
        self.wind_url_base = wind_url_base
        self.special_paths = special_paths

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
            u = self.get_user(uni)
            self.update_session(True,uni,groups,ticket_id,u.fullname())
            raise cherrypy.HTTPRedirect(self.after_login)

    def logout(self):
        self.update_session(False,"",[],"","")
        return
        
    def beforeMain(self):
        if self.is_testmode():
            return self.testmode()
        
        for p in self.strict_allowed_paths:
            if cherrypy.request.path.endswith == p:
                return
        
        for p in self.allowed_paths:
            if p in cherrypy.request.path:
                return

        for p in self.special_paths.keys():
            if cherrypy.request.path.endswith(p):
                return self.special_paths[p]()

        if cherrypy.request.path.endswith(self.login_url):
            return self.wind_login()

        if cherrypy.request.path.endswith(self.logout_url):
            return self.logout()
        if self.is_authenticated():
            return
        else:
            raise cherrypy.HTTPRedirect(self.login_url)

