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

    def test_ldap_lookup(self):
        (firstname,lastname) = ldap_lookup('anp8')
        assert firstname == 'Anders N.'
        assert lastname == 'Pearson'

        (firstname,lastname) = ldap_lookup('mbo2004')
        assert firstname == 'Melvyn Boon King'
        assert lastname == 'Ooi'
        print firstname, lastname

        (firstname,lastname) = ldap_lookup('bo2004')
        assert firstname == 'Brian R.'
        assert lastname == "O'Hagan Jr."
        print firstname, lastname



    def test_get_or_create_user(self):
        u = get_or_create_user("foo")
        assert u.firstname == self.user.firstname
        assert u.lastname == self.user.lastname

        # this one shouldn't be in the database yet
        u2 = get_or_create_user('anp8')
        assert u2.firstname == 'Anders N.'
        assert u2.lastname == 'Pearson'

class TestEcomap:
    def setup_class(self):
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test")
        self.course = Course(instructor=self.user,description="foo")
        self.map = Ecomap(name="test",description="test",flashData="blah blah blah",owner=self.user,course=self.course)

    def teardown_class(self):
        self.map.destroySelf()

    def test_basics(self):
        assert self.map.name == "test"
        assert self.map.description == "test"
        assert self.map.flashData == "blah blah blah"
        assert self.map.owner.uni == self.user.uni
        assert self.map.public == False



