from turbogears.tests import util
from ecomap.helpers import setup_for_tests, teardown_tests
from ecomap.model import Ecouser,Course,Ecomap
from ecomap.controllers import build_controllers
import unittest,cherrypy

from turbogears import database
database.set_db_uri("sqlite:///:memory:")

cherrypy.config.update({'global' : {'server.environment' : 'development', 'server.logToScreen' : False,
                                    'sessionFilter.on' : True, 'logDebugInfoFilter.on' : False}})
cherrypy.config.update({'global' : {'TESTMODE' : True}})

def setUp():
    setup_for_tests()
    build_controllers()
    
def tearDown():
    teardown_tests()

class EcoTest(unittest.TestCase):
    def setUp(self):
        setup_for_tests()
        # because create_ecomap hardcodes in a user:
        self.user = Ecouser(uni="foo",firstname="regression test user",lastname="test",securityLevel=1)
        self.course = Course(instructor=self.user,description="")
        self.user.addCourse(self.course)
    def tearDown(self):
        teardown_tests()



def GET(url,headers={}):
    util.createRequest(url,headers=headers)
    if cherrypy.response.headerMap['Content-Type'] == 'text/plain':
        return json_to_obj(cherrypy.response.body[0])
    else:
        return cherrypy.response.body[0]

import cStringIO as StringIO
def POST(url,data=""):
    rfile = StringIO.StringIO(data)
    util.createRequest(url,method="POST",rfile=rfile)
    return cherrypy.response

class TestRoot(EcoTest):
    def test_root(self):
        r = GET("/")
        assert "<title>" in r
        assert "Social Support Network Map" in r

    def test_create_ecomap(self):
        r = GET("/course/%d/create_new" % self.course.id)
        r = GET("/course/%d/" % self.course.id)
        assert "Enter Subject Name" in r

    def test_about(self):
        r = GET("/about")
        assert "Social Support Network Map" in r

    def test_help(self):
        r = GET("/help")
        assert "Social Support Network Map" in r

    def test_contact(self):
        r = GET("/contact")
        assert "Social Support Network Map" in r

    def test_mylist(self):
        r = GET("/myList")
        # should just be a redirect


        

class TestAdmin(EcoTest):
    def test_admin_users_form(self):
        r = GET("/admin_users_form")
        assert """<form action="admin_users" method="post">""" in r
        assert self.user.firstname in r
        assert self.user.lastname in r

    def test_create_course_form(self):
        r = GET("/create_course_form")
        assert "<form" in r
        assert '<input type="submit"' in r

    def test_create_course(self):
        POST("/create_course",
             data="name=newcourse;description=newcoursedescription;instructor=%d" % self.user.id)
        r = GET("/course/")
        assert "newcourse" in r

    def test_admin_users(self):
        u = Ecouser(uni="deleteme",firstname="deleteme",lastname="deleteme",securityLevel=2)
        POST("/admin_users",data="action=Change%%20Security%%20Level;user_id=%d" % u.id)
        assert u.is_admin()
        POST("/admin_users",data="action=Delete%%20Selected;user_id=%d" % u.id)
        assert u not in Ecouser.select()
        POST("/admin_users",data="action=Add%20User;user_uni=invaliduni")
        POST("/admin_users",data="action=Add%20Guest%20Account")



class TestCourse(EcoTest):

    def test_root(self):
        r = GET("/course/")
        assert '<form action="/update" method="post">' in r
        assert """<a href="/course/%d/">View Maps</a>""" % self.course.id in r
        assert """<a href="/course/%d/students">View Students</a>""" % self.course.id in r
        assert """<a href="/course/%d/edit_form">Edit Course Information</a>""" % self.course.id in r

    def test_edit_form(self):
        r = GET("/course/%d/edit_form" % self.course.id)
        assert """<form action="edit" method="post">""" in r

    def test_edit_course(self):
        POST("/course/%d/edit" % self.course.id,
             data="name=new%%20name;description=new%%20description;instructor=%d" % self.user.id)
        assert self.course.name == "new name"
        assert self.course.description == "new description"

    def test_maps(self):
        r = GET("/course/%d/" % self.course.id)
        assert "You have no Social Support Network Maps." in r
        assert """<a href="create_new">""" in r

    def test_students(self):
        r = GET("/course/%d/students" % self.course.id)
        assert self.user.firstname in r
        assert self.user.lastname in r

    def test_update_students(self):
        s = Ecouser(uni="deleteme", firstname="deletemefirst", lastname="deletemelast")
        s.addCourse(self.course)
        r = GET("/course/%d/students" % self.course.id)
        assert s.firstname in r
        assert s.lastname in r
        POST("/course/%d/update_students" % self.course.id,
             data="action=Delete%%20Selected;student_id=%d" % s.id)
        r = GET("/course/%d/students" % self.course.id)
        assert s.firstname not in r
        assert s.lastname not in r


    def test_create_map(self):
        for map in Ecomap.select():
            map.destroySelf()
        r = POST("/course/%d/create_new" % self.course.id) 
        r = GET("/course/%d/" % self.course.id)
        assert "You have no Social Support Network Maps." not in r
        assert "Enter Subject Name Here" in r
        assert "Enter Description here" in r
        assert "regression test user test" in r
        ecomap_id = self.course.ecomaps[0].id

        r = GET("/ecomap/%d/" % ecomap_id)
        assert str(ecomap_id) in r
        assert "<embed" in r
        
        POST("/course/%d/update" % self.course.id,data="ecomap_id=%d;action=share" % ecomap_id)

        POST("/course/%d/update" % self.course.id,data="ecomap_id=%d;action=Delete%%20Selected" % ecomap_id)
        r = GET("/course/%d/" % self.course.id)
        assert "You have no Social Support Network Maps." in r
        assert "Enter Subject Name Here" not in r
        assert "Enter Description here" not in r

    def test_delete_course(self):
        c = Course(name="deletethiscourse",instructor=self.user,description="")
        r = POST("/course/%d/delete" % c.id)
        r = GET("/course/")
        assert c.name not in r

class TestEcomap(EcoTest):
    def test_root(self):
        r = GET("/ecomap/")
        # should just be a redirect

	  


