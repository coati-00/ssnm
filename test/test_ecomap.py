import sys
sys.path.append(".")
import ecomap.config

ecomap.config.MODE = "regressiontest"
from ecomap.helpers import *

def setup_module(module):
    setup_for_tests()

def teardown_module(module):
    teardown_tests()

class TestEcouser:
        
    def setup_class(self):
        self.user = Ecouser(uni="foo",firstname="regression user",lastname="user")

    def teardown_class(self):
        self.user.destroySelf()

    def test_basics(self):
        assert self.user.uni == "foo"
        assert self.user.firstname == "regression user"
        assert self.user.lastname == "user"

class TestEcomap:
    def setup_class(self):
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test")
        self.map = Ecomap(name="test",description="test",flashData="blah blah blah",owner=self.user)

    def teardown_class(self):
        self.map.destroySelf()

    def test_basics(self):
        assert self.map.name == "test"
        assert self.map.description == "test"
        assert self.map.flashData == "blah blah blah"
        assert self.map.owner.uni == self.user.uni
        assert self.map.public == False



