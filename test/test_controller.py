import sys
sys.path.append(".")
import ecomap.config
ecomap.config.MODE = "regressiontest"
from ecomap.helpers import *
from ecomap.helpers.dummy_server import *
from ecomap.controller import start

def setup_module(module):
    setup_for_tests()

def teardown_module(module):
    teardown_tests()

class TestController:
    def setup_class(self):
        self.server = ServerCherrypy(start)
        self.server.setClientIP('127.0.0.1')
        self.server.setRequest('method','GET')
        self.server.setHeader('User-Agent','Lynx')
        self.server.setHeader('Host', 'ecomap.ccnmtl.columbia.edu')
        # because create_ecomap hardcodes in a user:
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test")

    def test_root(self):
        self.server.setPath("/")
        self.server.execute()
        assert self.server.getType() == 'text/html'
        assert self.server.getStatus()[0] == 200
        assert self.server.getResponse() != None

    def test_create_ecomap_form(self):
        self.server.setPath("/create_ecomap_form")
        self.server.execute()
        assert self.server.getType() == 'text/html'
        assert self.server.getStatus()[0] == 200
        assert self.server.getResponse() != None

    def test_create_ecomap(self):
        self.server.setPath("/create_ecomap?name=test%20ecomap&description=test%20description")
        self.server.execute()
        assert self.server.getStatus()[0] == 302
        assert self.server.getHeader('Location') == 'http://ecomap.ccnmtl.columbia.edu/myList'
        # now fetch the index again and make sure it appears in the list
        self.server.setPath("/myList")
        self.server.execute()
        assert "test ecomap" in self.server.getResponse()

    def test_create_ecomap_validation(self):
        """ try creating an ecomap without a name and make sure the form
        validation stops it with an error message """
        self.server.setPath("/create_ecomap")
        self.server.execute()
        assert self.server.getStatus()[0] == 200
        assert "Please enter a value" in self.server.getResponse()

       
