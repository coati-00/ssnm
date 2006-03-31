from turbogears.tests import util
from ecomap.helpers import *
import unittest

from turbogears import database
database.set_db_uri("sqlite:///:memory:")

class TestEcouser(unittest.TestCase):
        
    def setUp(self):
        setup_for_tests()
        self.user = Ecouser(uni="foo",firstname="regression user",lastname="user")

    def tearDown(self):
        self.user.destroySelf()
        teardown_tests()

    def test_basics(self):
        assert self.user.uni == "foo"
        assert self.user.firstname == "regression user"
        assert self.user.lastname == "user"
        assert self.user.fullname() == "regression user user"

    def test_toggle_admin(self):
        assert self.user.securityLevel == 2
        self.user.toggle_admin()
        assert self.user.securityLevel == 1
        self.user.toggle_admin()
        assert self.user.securityLevel == 2

    def test_ldap_lookup(self):
        (firstname,lastname) = ldap_lookup('anp8')
        assert firstname == 'Anders N.'
        assert lastname == 'Pearson'

        # this is a test to make sure the awesomest name ever
        # exists!
        (firstname,lastname) = ldap_lookup('mbo2004')
        assert firstname == 'Melvyn Boon King'
        assert lastname == 'Ooi'

        (firstname,lastname) = ldap_lookup('bo2004')
        assert firstname == 'Brian R.'
        assert lastname == "O'Hagan Jr."

    def test_get_or_create_user(self):
        u = get_or_create_user("foo")
        assert u.firstname == self.user.firstname
        assert u.lastname == self.user.lastname

        # this one shouldn't be in the database yet
        u2 = get_or_create_user('anp8')
        assert u2.firstname == 'Anders N.'
        assert u2.lastname == 'Pearson'

    def test_create_user(self):
        u = create_user('mbo2004')
        assert u.firstname == 'Melvyn Boon King'
        assert u.lastname == 'Ooi'

        u2 = create_user('foo')
        assert u2.firstname == self.user.firstname
        assert u2.lastname == self.user.lastname

        try:
            u3 = create_user('iamaninvaliduni')
            assert 1 == 0
        except InvalidUNI:
            assert 1 == 1

    def test_delete(self):
        u = Ecouser(uni="bar",firstname="deleteme",lastname="deleteme")
        all = list(Ecouser.select())
        assert u in all
        u.delete()
        all = list(Ecouser.select())
        assert u not in all
        


class TestEcomap(unittest.TestCase):
    def setUp(self):
        setup_for_tests()
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test")
        self.course = Course(instructor=self.user,description="foo")
        self.map = Ecomap(name="test",description="test",flashData="blah blah blah",owner=self.user,course=self.course)

    def tearDown(self):
        self.map.destroySelf()
        teardown_tests()

    def test_basics(self):
        assert self.map.name == "test"
        assert self.map.description == "test"
        assert self.map.flashData == "blah blah blah"
        assert self.map.owner.uni == self.user.uni
        assert self.map.public == False

    def testLoad(self):
        r = self.map.load(readonly="true")
        assert r == """<data><response>OK</response><isreadonly>true</isreadonly><name>test</name><description>test</description>blah blah blah</data>"""

    def testSave(self):
        pass # TODO



class TestCourse(unittest.TestCase):
    def setUp(self):
        setup_for_tests()
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test")
        self.course = Course(instructor=self.user,description="foo")

    def tearDown(self):
        teardown_tests()

    def test_delete(self):
        r = get_all_courses()
        assert self.course in r
        self.course.delete()
        r = get_all_courses()
        assert self.course not in r

    def test_add_student(self):
        u = Ecouser(uni="bar",firstname="new",lastname="student")
        self.course.add_student(u.uni)

        # try adding the instructor
        self.course.add_student(self.user.uni)

        




