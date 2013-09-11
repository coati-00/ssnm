from django.db import models

class Ecomap(models.Model):
    name = models.CharField(max_length=50)

    def set_map_name(self, given_name):
        name = given_name

    def __unicode__(self):
        return self.name



