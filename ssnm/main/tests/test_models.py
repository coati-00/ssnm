'''Test the almost nonexistant methods within the model classes'''

from ssnm.main.models import Ecomap, EcomapManager
from ssnm.main.views import *
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

class TestModels(TestCase):

    def setup(self):
        self.user = User.objects.create_user('somestudent', 'email@email.com', 'somestudent')
        self.user.save()
        self.ecomap = User.objects.create_ecomap(owner=self.user)
        self.ecomap.save()

    def test_ecomap_manager(self):
    	pass
    	#print self.ecomap.owner
    	#print self.user
        #self.assertEqual(self.ecomap.owner, self.user)



