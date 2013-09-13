'''
This file is to test all the views of the application.
'''
from django.utils import unittest
from ecomap.models import *
from ecomap.views import *
from django.test.client import Client
from ecomap.urls import *
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

class ViewTest(TestCase): # unittest.

    def setUp(self):
        #self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('somestudent', 'email@email.com', 'somestudent')
        self.user.ecouser = Ecouser(status='ST', uni='444', user_id='679')
        self.user.ecouser.save()
        self.user.save()
        #IF BELOW VIEWS ARE COMMENTED OUT ALMOST EVERYTHING PASSES
        self.ecomap = Ecomap(pk='6', name="Test Map 1", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>somestudent</name><flashData><circles><circle><radius>499</radius></circle><circle><radius>350</radius></circle><circle><radius>200</radius></circle></circles><supportLevels><supportLevel><text>VeryHelpful</text></supportLevel><supportLevel><text>SomewhatHelpful</text></supportLevel><supportLevel><text>NotSoHelpful</text></supportLevel></supportLevels><supportTypes><supportType><text>Social</text></supportType><supportType><text>Advice</text></supportType><supportType><text>Empathy</text></supportType><supportType><text>Practical</text></supportType></supportTypes><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>")
        self.ecomap.owner_id = '444'
        self.ecomap.save()


#     # FIRST CHECK THAT ALL URLS ARE ACCESSIBLE
#     # following three pass whether using client or the above user info
#     def test_about(self):
#         response = self.client.get('/ecomap/about/')
#         self.assertEqual(response.status_code, 200)


#     def test_help(self):
#         response = self.client.get('/ecomap/help/')
#         self.assertEqual(response.status_code, 200)


#     def test_contact(self):
#         response = self.client.get('/ecomap/contact/')
#         self.assertEqual(response.status_code, 200)


#     # MUST LOG ON TO SEE OTHER VIEWS
#     def test_login_page(self):
#         response = self.client.post('', { 'username' : 'somestudent', 'password':'somestudent'})
#         self.assertEqual(response.status_code, 200)

#     # AFTER LOGGING IN MAKE SURE THAT THE HOME PAGE IS ACCESSIBLE TO THE CURRENT USER
#     def test_home_page(self):
#         request = self.factory.post('/ecomap/show_maps/')
#         request.user = self.user
#         response = show_maps(request)
#         self.assertEqual(response.status_code, 200)

# # CHANGING THESE TO TAKE CARE OF DECORATOR
#     #TEST WITH NO SAVE MAP - CREATE NEW MAP
#     def test_ecomap(self):
#         request = self.factory.post('/ecomap/ecomap/')
#         request.user = self.user
#         response = ecomap(request)
#         self.assertEqual(response.status_code, 200)
#         #self.client.login(username='somestudent', password='somestudent')
#         #response = self.client.post('/ecomap/ecomap/')
#         #self.assertEqual(response.status_code, 200)

#     #TEST RETRIEVAL OF SAVE MAP
#     def test_saved_ecomap(self):
#         request = self.factory.post('/ecomap/ecomap/6/')
#         request.user = self.user
#         response = get_map(request)
#         self.assertEqual(response.status_code, 200)
# #        self.client.login(username='somestudent', password='somestudent')
# #        response = self.client.post('/ecomap/ecomap/6/')
# #        self.assertEqual(response.status_code, 200)


# #TEST FLASH IS RETURNING XML
#     def test_flash_ecomap(self):
#         request = self.factory.post('/ecomap/ecomap/display/flashConduit')
#         request.user = self.user
#         response = show_maps(request)
#         self.assertEqual(response.status_code, 200)

#     def test_saved_flash_ecomap(self):
#         request = self.factory.post('/ecomap/ecomap/6/display/flashConduit')
#         request.user = self.user
#         response = show_maps(request)
#         self.assertEqual(response.status_code, 200)
