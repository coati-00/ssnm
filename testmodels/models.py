from django.db import models

class Ecouser(models.Model):
    USER_STATUS_CHOICES = (
        ('IN', 'Instructor'),
        ('ST', 'Student'),
        ('AD', 'Administrator'),
    )
    uni = models.CharField(max_length=50, unique=True) #should I make uni the primary key or are their rare instances where this would be an issue?
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    user_status = models.CharField(max_length=2, choices=USER_STATUS_CHOICES)


    def __unicode__(self):
        full_info = self.firstname + " " + self.lastname + " " + self.uni
        return full_info

    def user_name(self):
        return self.firstname + " " + self.lastname

    def user_status(self):
        if self.user_status:
            return self.user_status
        else:
            return "unknown"

class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100) #other model sets default to ""
    description = models.CharField(max_length=200) #other model sets default to ""
    users = models.ManyToManyField('Ecouser')
    def get_all_users(course_id):
        pass

    def __unicode__(self):
        full_info = self.name + " " + self.description + " " + self.course_id #+ " " + str(self.instructor)
        return full_info
