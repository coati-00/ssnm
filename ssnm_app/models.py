from django.db import models
from django.utils import timezone
#from django.forms import ModelForm
#from datetime import datetime as DateTime #?

class Ecouser(models.Model):
    USER_STATUS_CHOICES = (
        ('IN', 'Instructor'),
        ('ST', 'Student'),
        ('AD', 'Administrator'),
    )
    uni = models.CharField(max_length=50, unique=True) #should I make uni the primary key or are their rare instances where this would be an issue?
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    participantOf = models.CharField(max_length=10) #could be instructor or student - need to keep track of who is in which course these are many to many
    courses = models.CharField(max_length=50) # do I need this?
    user_status = models.CharField(max_length=2, choices=USER_STATUS_CHOICES)








    def __unicode__(self):
        full_info = self.firstname + " " + self.lastname + " " + self.uni
        return full_info

    def user_name(self):
        return self.firstname + " " + self.lastname

    def user_status(self):
        if user_status:
            return self.user_status
        else:
            return "unknown"



class Course(models.Model):
    course_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100) #other model sets default to ""
    description = models.CharField(max_length=200) #other model sets default to ""
    users = models.ManyToManyField('Ecouser') #each course has 1 instructor
    #is it possible to also have an owner setto models.ForiegnKeyFile('Ecouser')
    #students - need way to gather all students of course
    # HOW TO  SPECIFY THAT COURSE REQUIRES USES
    def __unicode__(self):
        full_info = self.name + " " + self.description + " " + self.course_id #+ " " + str(self.instructor)
        return full_info

#    def public_ecomaps(self):
#        Ecomaps.objects.get(course=self.course_id)

#    def course_ecomaps():


#    def course_instructor(self):
#        return self
#how to specify users based on status

#    def course_students():



class Ecomap(models.Model):
    ecomap_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    created = models.DateTimeField(default=timezone.now())
    modified = models.DateTimeField(default=timezone.now())
    course = models.ForeignKey('Course') # each ecomap belongs to a course
    owner = models.ForeignKey('Ecouser') # an ecomap must have an owner or creator
    def __unicode__(self):
        full_info = self.ecomap_id + " " + self.name + " " + self.description + " " + self.course + " " + self.owner + " " + self.course
        return full_info



# #Forms for the models - was not clear from django site if they should live here or if they should live in the views
# class CourseForm(ModelForm):
#     class Meta:
#         model = Course

# class Ecouser(ModelForm):
#     class Meta:
#         model = Ecouser

# class Ecomap(ModelForm):
#     class Meta:
#         model = Ecomap






        
