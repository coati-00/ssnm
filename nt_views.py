from django.utils import unittest
from ecomap.models import Ecouser
from ecomap.views import *
from django.test.client import Client


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get('ecomap/ecomap/')
        self.assertEqual(response.status_code, 200)
        #test context

    def test_about(self):
        response = self.client.get('ecomap/about/')
        self.assertEqual(response.status_code, 200)

    def test_help(self):
        response = self.client.get('ecomap/help/')
        self.assertEqual(response.status_code, 200)

    # def test_login(self,uni="",password=""):
    #     response = self.client.get('ecomap/ecomap')
    #     self.assertEqual(response.status_code, 200)

    def test_contact(self):
        response = self.client.get('ecomap/contact/')
        self.assertEqual(response.status_code, 200)

#    def test_home_page(request):


    def test_show_students(self):
        response = self.client.get('ecomap/234/show_students/')
        self.assertEqual(response.status_code, 200)

    def test_user_courses(self):
        response = self.client.get('ecomap/34567/user_courses/')
        self.assertEqual(response.status_code, 200)

#    def test_show_course_students(request, course):

    def test_add_course(self):
        response = self.client.get('ecomap/add_course/')
        self.assertEqual(response.status_code, 200)

