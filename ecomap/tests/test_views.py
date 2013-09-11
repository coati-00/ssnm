from django.utils import unittest
from ecomap.models import Ecouser
from ecomap.views import *
from django.test.client import Client


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()


    # FIRST CHECK THAT ALL URLS ARE ACCESSIBLE


    def test_about(self):
        response = self.client.get('ecomap/about/')
        self.assertEqual(response.status_code, 200)


    def test_help(self):
        response = self.client.get('ecomap/help/')
        self.assertEqual(response.status_code, 200)


    def test_contact(self):
        response = self.client.get('ecomap/contact/')
        self.assertEqual(response.status_code, 200)


#    def test_student_home(self):
#        response = self.client.get('ecomap/home/')
#        self.assertEqual(response.status_code, 200)
        #test context

    # MUST LOG ON TO SEE OTHER VIEWS
    def test_login_page(self):
        response = self.client.post('', { 'username' : 'somestudent', 'password':'somestudent'})
        self.assertEqual(response.status_code, 200)

    # AFTER LOGGING IN MAKE SURE THAT THE HOME PAGE IS ACCESSIBLE TO THE CURRENT USER
    def test_home_page(self):
        response = self.client.post('/ecomap/show_maps/')
        self.assertEqual(response.status_code, 200)

    #TEST WITH NO SAVE MAP - CREATE NEW MAP
    def test_ecomap(self):
        response = self.client.post('/ecomap/ecomap/')
        self.assertEqual(response.status_code, 200)

    #TEST RETRIEVAL OF SAVE MAP
    def test_saved_ecomap(self):
        response = self.client.post('/ecomap/ecomap/6/')
        self.assertEqual(response.status_code, 200)


    # CHECK THAT ALL URLS SHOW APPROPRIATE CONTENT
    



    # CHECK THAT