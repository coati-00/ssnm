import sys
sys.path.append(".")
import ecomap.config
import unittest

ecomap.config.MODE = "regressiontest"
from ecomap.helpers import *

def setup_module(module):
    setup_for_tests()

def teardown_module(module):
    teardown_tests()

class TestEcouser(unittest.TestCase):
        
    def setup_class(self):
        self.user = Ecouser(uni="foo",name="regression test user")

    def teardown_class(self):
        self.user.destroySelf()

    def test_basics(self):
        assert self.user.uni == "foo"
        assert self.user.name == "regression test user"

class TestEcomap(unittest.TestCase):
    def setup_class(self):
        self.user = Ecouser(uni="foo",name="regression test user")
        self.map = Ecomap(name="test",description="test",flashData="blah blah blah",owner=self.user)

    def teardown_class(self):
        self.map.destroySelf()

    def test_basics(self):
        assert self.map.name == "test"
        assert self.map.description == "test"
        assert self.map.flashData == "blah blah blah"
        assert self.map.owner.uni == self.user.uni
        assert self.map.public == False


def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestEcouser))
    suite.addTest(loader.loadTestsFromTestCase(TestEcomap))
    return suite
       
