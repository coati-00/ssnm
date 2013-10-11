'''Test the almost nonexistant methods within the model classes'''

from ssnm.main.models import Ecomap
from django.contrib.auth.models import User
from django.test import TestCase


class TestModels(TestCase):
    def setup(self):
        self.user = User.objects.create_user(
            'somestudent', 'email@email.com', 'somestudent')
        self.user.save()
        self.ecomap = Ecomap.objects.create_ecomap(owner=self.user)
        self.ecomap.save()

    def test_ecomap_manager(self):
        user = User.objects.create_user(
            'somestudent', 'email@email.com', 'somestudent')
        user.save()
        ecomap = Ecomap.objects.create_ecomap(owner=user)
        ecomap.save()
        self.assertEqual(ecomap.owner, user)
