'''
This file is to test all the views of the application.
'''
from django.db import models
from ssnm.main.models import Ecomap, EcomapManager, CreateAccountForm
from ssnm.main.views import *
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from registration.forms import RegistrationForm
from django import forms



class ViewTest(TestCase):  # unittest.

    def setUp(self):
        '''Set up method for testing views.'''
        self.factory = RequestFactory()
        self.user = User.objects.create_user('somestudent', 'email@email.com', 'somestudent')
        self.user.save()
        #IF BELOW VIEWS ARE COMMENTED OUT ALMOST EVERYTHING PASSES
        self.ecomap = Ecomap(pk='6', name="Test Map 1", ecomap_xml="<data><response>OK</response><isreadonly>false</isreadonly><name>somestudent</name><flashData><circles><circle><radius>499</radius></circle><circle><radius>350</radius></circle><circle><radius>200</radius></circle></circles><supportLevels><supportLevel><text>VeryHelpful</text></supportLevel><supportLevel><text>SomewhatHelpful</text></supportLevel><supportLevel><text>NotSoHelpful</text></supportLevel></supportLevels><supportTypes><supportType><text>Social</text></supportType><supportType><text>Advice</text></supportType><supportType><text>Empathy</text></supportType><supportType><text>Practical</text></supportType></supportTypes><persons><person><name>green</name><supportLevel>2</supportLevel><supportTypes><support>Advice</support><support>Social</support></supportTypes><x>293</x><y>70</y></person><person><name>yellow</name><supportLevel>1</supportLevel><supportTypes><support>Social</support><support>Empathy</support></supportTypes><x>448</x><y>208</y></person><person><name>red</name><supportLevel>0</supportLevel><supportTypes><support>Social</support><support>Practical</support></supportTypes><x>550</x><y>81.95</y></person></persons></flashData></data>")
        self.ecomap.owner = self.user
        self.ecomap.save()
        #unauthenticated user
        self.bad_user = User.objects.create_user('not_ecouser', 'email@email.com', 'not_ecouser')
        self.bad_user.save()


    # FIRST CHECK THAT ALL URLS ARE ACCESSIBLE
    # following three pass whether using client or the above user info
    def test_about(self):
        '''Test that requesting about page returns a response.'''
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('about.html')

    def test_help(self):
        '''Test that requesting help page returns a response.'''
        response = self.client.get('/help/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('help.html')


    def test_contact(self):
        '''Test that requesting contact page returns a response.'''
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contact.html')

    def test_thanks(self):
        '''Test that requesting thanks page returns a response.'''
        response = self.client.get('/thanks/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('thanks.html')


    #  user must be logged in the see the other views
    # we also should check that logged in usrs can access the views not requiring authentication
    def test_user_about(self):
        '''Test that user requesting about page returns a response.'''
        request = self.factory.post('/about/')
        request.user = self.user
        response = about(request)
        self.assertEqual(response.status_code, 200)


    def test_user_help(self):
        '''Test that user requesting help page returns a response.'''
        request = self.factory.post('/help/')
        request.user = self.user
        response = help_page(request)
        self.assertEqual(response.status_code, 200)


    def test_user_contact(self):
        '''Test that user requesting contact page returns a response.'''
        request = self.factory.post('/contact/')
        request.user = self.user
        response = contact(request)
        self.assertEqual(response.status_code, 200)


    # FORMS
    # Now we must deal with the forms - CreateAccountForm, LoginFor, ContactForm, EcomapForm
    def test_create_account(self):
        '''Test that user who creates account get appropriate response.'''
        request = self.factory.post('/create_account/', {"first_name" : "firstname", "last_name" : "lastname", "username" : "username", "email" : "test_email@email.com","password1" : "password", "password2" : "password"})
        response = create_account(request)
        self.assertEqual(response.status_code, 302)

    def test_validation_one_create_account(self):
        with self.assertRaises(forms.ValidationError):
            '''Test that user who creates account with already existing username triggers exception handling.'''
            request = self.factory.post('/create_account/', {"first_name" : "firstname", "last_name" : "lastname", "username" : "somestudent", "email" : "test_email@email.com","password1" : "password", "password2" : "password"})
            response = create_account(request)



    def test_validation_two_create_account(self):
        with self.assertRaises(forms.ValidationError):
            '''Test that user who creates account with different passwords triggers exception handling.'''
            request = self.factory.post('/create_account/', {"first_name" : "firstname", "last_name" : "lastname", "username" : "username", "email" : "test_email@email.com", "password1" : "password1", "password2" : "password"})
            response = create_account(request)


    def test_validation_three_create_account(self):
        with self.assertRaises(forms.ValidationError):
            '''Test that user who creates account a missing password triggers exception handling.'''
            request = self.factory.post('/create_account/', {"first_name" : "some_rand_name", "last_name" : "some_rand_name", "username" : "unknownstudent", "email" : "test_email@email.com", "password2" : "password"})
            response = create_account(request)

    # Contact Form
    def test_contact_form(self):
        request = self.factory.post('/contact/', {"subject" : "subject here", "message" : "message here", "sender" : "sender", "recipients" : "test_email@email.com"})
        response = contact(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('thanks.html')



    #set details for a map
    # def test_details(self):
    #     '''Test that user who creates account get appropriate response.'''
    #     request = self.factory.post('/details/6/', {"name" : "Test Map Name Here", "description" : "Make sure description box takes input"})
    #     request.user = self.user
    #     response = get_map_details(request, 6)
    #     self.assertEqual(response.status_code, 200)

    def test_details_empty_form(self):
        '''Test that user who creates account get appropriate response.'''
        request = self.factory.get('/details/6/')
        request.user = self.user
        response = get_map_details(request, 6)
        self.assertEqual(response.status_code, 200)


    def test_show_maps(self):
        '''Test that logged in user recieves response of home page..'''
        request = self.factory.post('/show_maps/')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)


    # #  TEST RETRIEVAL OF SAVE MAP
    # def test_saved_ecomap(self):
    #     '''Test that requesting saved_ecomap page returns a response.'''
    #     request = self.factory.post('/ecomap/6/')
    #     request.user = self.user
    #     response = get_map(request, 6)
    #     self.assertEqual(response.status_code, 200)


    def test_delete_map(self):
        request = self.factory.post('/delete_map/6/')
        request.user = self.user
        response = delete_map(request, 6)
        with self.assertRaises(Ecomap.DoesNotExist):
            ecomap = Ecomap.objects.get(pk=6)


    def test_logout(self):
        request = self.factory.post('/logout/')
        request.user = self.user
        response = logout(request)
        self.assertEqual(response.status_code, 302)
        #self.assertRedirects(response, '/accounts/logout/')


# TEST FLASH IS RETURNING RESPONSE
    def test_flash_ecomap(self):
        '''Test that requesting ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)


    def test_saved_flash_ecomap(self):
        '''Test that requesting saved_ecomap_page's flash conduit
        returns a response.'''
        request = self.factory.post('/ecomap/6/display/flashConduit')
        request.user = self.user
        response = show_maps(request)
        self.assertEqual(response.status_code, 200)


    def test_saved_flash(self):
        request = self.factory.post('/ecomap/6/display/flashConduit')
        request.user = self.user
        response = display(request, 6)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('game_test.html')


    # def test_get_map(self):
    #     request = self.factory.post('/ecomap/')
    #     request.user = self.user
    #     response = get_map(request, "")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed('game_test.html')


    #THIS MUST BE DONE
    # def test_login(self):
    #     '''Test that user can login through login form.'''
    #     request = self.factory.post('', {"username" : "somestudent", "password" : "somestudent"})
    #     response = my_login(request)
    #     #self.assertEqual(response.status_code, 302)
    #     #self.assertRedirects(response, "/show_maps/")

    # def test_login_one_error(self):
    #     with self.assertRaises(forms.ValidationError):
    #         '''Test that user who tries to login and does not have an account triggers exception handling.'''
    #         request = self.factory.post('', {"username" : "no_username", "password" : "password"})
    #         response = my_login(request)

    # def test_login_two_error(self):
    #     with self.assertRaises(forms.ValidationError):
    #         '''Test that user who enters wrong password triggers exception handling.'''
    #         request = self.factory.post('', {"username" : "somestudent", "password" : "bad_password"})
    #         response = my_login(request)

    # if request.method == 'POST':
    #     form = LoginForm(request.POST)
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     user = authenticate(username=username, password=password)
    #     #print user.username
    #     if user is not None:
    #         if user.is_active:
    #             login(request, user)
    #             return HttpResponseRedirect('/show_maps/')
    #         else:
    #             return HttpResponseRedirect('It appears you do not have an account, please create one to use this application')
    #     else:
    #         forms.ValidationError('It appears you do not have an account, please create one to use this application')
    # else:
    #     form = LoginForm()  # An unbound form

    # return render(request, 'login.html', {
    #     'form': form,
    # })
        # response, the name of template used for form, form field in question, error text
        #self.assertValidationError(response, "RegistrationForm", 'username', 'this username already exists')
        #self.assertRaises(forms.ValidationError("this username already exists"))
        #self.assertTemplateUsed('create_account.html')


    # def test_login_page(self):
    #     '''Test that created user logging in returns a page.'''
    #     request = self.client.post('', { 'username' : 'somestudent', 'password' : 'somestudent'})
    #     response = login(request)
    #     self.assertEqual(response.status_code, 200)


# ###########################
# # CHECK THAT VIEWS ARE NOT RETURNED TO NON ECOMAP USER


    # def test_fail_show_maps_page(self):
    #     '''We want to make sure that users who may have unis but
    #     are not actually ecomap users cannot cannot access maps.'''
    #     request = self.factory.post('/show_maps/')
    #     request.user = self.bad_user
    #     response = show_maps(request)
    #     self.assertEqual(response.status_code, 401)


    # def test_fail_saved_ecomap(self):
    #     '''We want to make sure that users who may have unis but
    #     are not actually ecomap users cannot cannot access other
    #     users saved maps.'''
    #     request = self.factory.post('/ecomap/6/')  # WSGI Request
    #     request.user = self.bad_user
    #     response = get_map(request, 6)
    #     self.assertEqual(response.status_code, 401)


    # def test_fail_flash_ecomap(self):
    #     '''We want to make sure that users who may have unis but
    #     are not actually ecomap users cannot cannot access flash conduit.'''
    #     request = self.factory.post('/ecomap/display/flashConduit')
    #     request.user = self.bad_user
    #     response = show_maps(request)
    #     self.assertEqual(response.status_code, 401)


    # def test_fail_saved_flash_ecomap(self):
    #     '''We want to make sure that users who may have unis but
    #     are not actually ecomap users cannot cannot access flash
    #     conduit for saved maps.'''
    #     request = self.factory.post('/ecomap/6/display/flashConduit')
    #     request.user = self.bad_user
    #     response = show_maps(request)
    #     self.assertEqual(response.status_code, 401)


    # def test_user_request_map_that_does_not_exist(self):
    #     '''We should check that when a user requests a map that does
    #     not exist in the url an appropriate response is given.'''
    #     request = self.client.post('/ecomap/7/')
    #     request.user = self.user
    #     response = get_map(request)
    #     self.assertEqual(response.status_code, 404)



