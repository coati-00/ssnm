'''
This is a test file to see if changing what libraries are used for testing will effect how jenkins responds to percieved coverage.
'''
from django.test import TestCase
from django.test.client import Client

class SimpleViewTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_about(self):
        '''Test that requesting about page returns a response.'''
        response = self.client.get('/ecomap/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('about.html')

    def test_help(self):
        '''Test that requesting help page returns a response.'''
        response = self.client.get('/ecomap/help/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('help.html')

    def test_contact(self):
        '''Test that requesting contact page returns a response.'''
        response = self.client.get('/ecomap/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('contact.html')