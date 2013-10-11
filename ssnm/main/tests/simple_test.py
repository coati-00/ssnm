'''
This is a test file to see if changing what libraries are
used for testing will effect how jenkins responds to percieved coverage.
'''
from django.test import TestCase
from django.test.client import Client


class SimpleViewTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_about(self):
        '''Test that requesting about page returns a response.'''
        response = self.c.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('about.html')

    def test_help(self):
        '''Test that requesting help page returns a response.'''
        response = self.c.get('/help/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('help.html')

    def test_contact(self):
        '''Test that requesting contact page returns a response.'''
        response = self.c.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contact.html')

    def test_home_page(self):
        '''Test that user recieves response of home page.'''
        response = self.c.get('')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('/login.html')

    def test_create_user_account(self):
        '''Test user submitting form to create account.'''
        submit = self.c.post(
            '/contact/',
            {'firstname': 'firstname', 'lastname': 'lastname',
             'username': 'username', 'password1': 'password',
             'password2': 'password'})
        self.assertEqual(submit.status_code, 200)
        self.assertTemplateUsed('/contact.html')
