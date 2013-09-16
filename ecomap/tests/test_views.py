'''
This file is to test all the views of the application.
'''
#from django.utils import unittest
from ecomap.models import Ecouser, Ecomap
from ecomap.views import ecomap, get_map, show_maps, ContactForm, CreateAccountForm, FeedbackForm, EcomapForm, logout, guest_login, contact, about, help_page, home
#from django.test.client import Client
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


class ViewTest(TestCase):  # unittest.

    def setUp(self):
        '''Set up method for testing views.'''
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
        #unauthenticated user
        self.bad_user = User.objects.create_user('not_ecouser', 'email@email.com', 'not_ecouser')
        self.bad_user.save()

    # FIRST CHECK THAT ALL URLS ARE ACCESSIBLE
    # following three pass whether using client or the above user info
    def test_about(self):
        '''Test that requesting about page returns a response.'''
        response = self.client.get('/ecomap/about/')
        self.assertEqual(response.status_code, 200)

    def test_help(self):
        '''Test that requesting help page returns a response.'''
        response = self.client.get('/ecomap/help/')
        self.assertEqual(response.status_code, 200)

    def test_contact(self):
        '''Test that requesting contact page returns a response.'''
        response = self.client.get('/ecomap/contact/')
        self.assertEqual(response.status_code, 200)

    def test_create_account(self):
        '''Test that user who creates account get appropriate response.'''
        pass

    def test_create_guest_account(self):
        '''Test that guest user who creates account is returned an appropriate resposne.'''
        pass


    #  user must be logged in the see the other views
    # we also should check that logged in usrs can access the views not requiring authentication
    def test_user_about(self):
        '''Test that user requesting about page returns a response.'''
        request = self.factory.post('/ecomap/about/')
        request.user = self.user
        response = about(request)
        self.assertEqual(response.status_code, 200)

    def test_user_help(self):
        '''Test that user requesting help page returns a response.'''
        request = self.factory.post('/ecomap/help/')
        request.user = self.user
        response = help_page(request)
        self.assertEqual(response.status_code, 200)

    def test_user_contact(self):
        '''Test that user requesting contact page returns a response.'''
        request = self.factory.post('/ecomap/contact/')
        request.user = self.user
        response = contact(request)
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        '''Test that created user logging in returns a page.'''
        response = self.client.post('', { 'username' : 'somestudent', 'password' : 'somestudent'})
        self.assertEqual(response.status_code, 200)

    def guest_login_page(self):
        '''Test that guest user who created an account is returned a page upon logging in.'''
        pass
        #response = self.client.post('', { 'username' : 'guestuser', 'password' : 'guestuser'})
        #self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        '''Test that logged in user recieves response of home page..'''
        request = self.factory.post('/ecomap/show_maps/')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

    def test_ecomap(self):
        '''See that ecomap page returns response.'''
        request = self.factory.post('/ecomap/ecomap/')
        request.user = self.user
        response = ecomap(request)
        self.assertEqual(response.status_code, 200)

    #  TEST RETRIEVAL OF SAVE MAP
    def test_saved_ecomap(self):
        '''Test that requesting saved_ecomap page returns a response.'''
        print "inside method"
        request = self.factory.post('/ecomap/ecomap/6/')  # WSGI Request
        request.user = self.user  # User
        response = get_map(request, 6)
        print type(response)
        self.assertEqual(response.status_code, 200)

# TEST FLASH IS RETURNING RESPONSE
    def test_flash_ecomap(self):
        '''Test that requesting ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/ecomap/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

    def test_saved_flash_ecomap(self):
        '''Test that requesting saved_ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/ecomap/6/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)

# ###########################
# # CHECK THAT VIEWS ARE NOT RETURNED TO NON ECOMAP USER
    def test_fail_login_page(self):
        '''We want to make sure that users who may have unis but
        are not actually ecomap users cannot login.'''
        response = self.bad_user.post('', { 'username' : 'not_ecouser', 'password' : 'not_ecouser'})
        self.assertEqual(response.status_code, 401)

    def test_fail_show_maps_page(self):
        '''We want to make sure that users who may have unis but
        are not actually ecomap users cannot cannot access maps.'''
        request = self.factory.post('/ecomap/show_maps/')
        request.user = self.bad_user
        response = show_maps(request)
        self.assertEqual(response.status_code, 401)

    def test_fail_saved_ecomap(self):
        '''We want to make sure that users who may have unis but
        are not actually ecomap users cannot cannot access other
        users saved maps.'''
        print "inside method"
        request = self.factory.post('/ecomap/ecomap/6/')  # WSGI Request
        request.user = self.bad_user  # User
        response = get_map(request, 6)
        print type(response)
        self.assertEqual(response.status_code, 401)

    def test_fail_flash_ecomap(self):
        '''We want to make sure that users who may have unis but
        are not actually ecomap users cannot cannot access flash conduit.'''
        request = self.factory.post('/ecomap/ecomap/display/flashConduit')
        request.user = self.bad_user
        response = show_maps(request)
        self.assertEqual(response.status_code, 401)

    def test_fail_saved_flash_ecomap(self):
        '''We want to make sure that users who may have unis but
        are not actually ecomap users cannot cannot access flash
        conduit for saved maps.'''
        request = self.factory.post('/ecomap/ecomap/6/display/flashConduit')
        request.user = self.bad_user
        response = show_maps(request)
        self.assertEqual(response.status_code, 401)
