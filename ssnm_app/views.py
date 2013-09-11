#views based on @expose meta tags from controllers.py from original ecomap program
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import Context, loader
from django import forms
from django.views.generic.edit import FormView
from ssnm_app.models import Course, Ecouser, Ecomap
from django.forms import ModelForm


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(max_length=200)
    sender = forms.EmailField()


class FeedbackForm(forms.Form):
    subject = forms.CharField(max_length=100)    
    message = forms.CharField(max_length=200)
    sender = forms.EmailField()

class CourseForm(forms.Form):
    course_id = forms.CharField(max_length=10)
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=200)
    instructor = forms.CharField(max_length=50)
    #users

def index(request):
    """Simply direct user to index/default page."""
    return render_to_response('ssnmapp/index.html')


def about(request):
    """Simply returns about page."""
    return render_to_response('ssnm_app/about.html')


def help(request):
    """Returns help page."""
    return render_to_response('ssnm_app/help.html')

def login(self,uni="",password=""):
    """Presents login page."""
    return render_to_response("guest_login.html")


# def contact(request):#got from django site should probably redo
#     """Redirects to contact page."""
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             subject = form.cleaned_data['subject']
#             message = form.cleaned_data['message']
#             sender  = form.cleaned_data['sender']
#             recipients = ['some_email@somewhere.com']
#             from django.core.mail import send_mail
#             send_mail(subject, message, recipients)
#             return HttpResponseRedirect('/thanks/')
#     else:
#         form = ContactForm()

#     return render(request,'contact.html', {
#         'form': form,
#     })
def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['someone@somewhere.com']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })

#Homepage should be login or overview screen no a list of courses
def home_page(request):
    """Displays homepage."""
    list_courses = Course.objects.order_by('name') #this prints the objects not their names
    put_in_page = ''.join([c.name + "          " + c.description + "<br>"  for c in list_courses])
    return HttpResponse(put_in_page)


#if user clicks on view students link on home page they are directed to a page with three columns: first name, last name, uni
#correctly shows the list of students sorted by their last name
def show_students(request):
    """Show all students, ordered by name."""
    list_students = Ecouser.objects.order_by('lastname') #this prints the objects not their names
    put_in_page = ''.join([c.firstname + "          " + c.lastname +  "<br>"  for c in list_students])
    return HttpResponse(put_in_page)


def user_courses(request, user_uni):
    """List all courses associated with a particular user."""
    student = Ecouser.objects.get(uni=user_uni)
    course_list = student.course_set.all()
    put_on_page = ''.join([c.name + "          " + c.description +  "<br>"  for c in course_list])
    return HttpResponse(put_on_page)


#THIS IS HOW YOU GO ACCROSS TABLES IN DJANGO
def show_course_students(request, course):
    """Show all students enrolled in a particular course."""
    course = Course.objects.get(course_id=course)
    students = course.users.all()
    put_on_page = ''.join([c.firstname + " " + c.lastname + " " + c.uni + "<br>"  for c in students])
    return HttpResponse(put_on_page)


def add_course(request):
    """Allow admin or instructor to add a new course to the application"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course_id']
            c_name = form.cleaned_data['name']
            c_description = form.cleaned_data['description']
            c_instructor = form.cleaned_data['instructor']
            course = Course(course_id=course, name=c_name, description=c_description, instructor=c_instructor)
            course.save()
            #dc = Course.ojects.get(course_id=course)
            #put_on_page = ''.join([c.course_id + "          " + c.name + "          " + c.description + "          " + c.instructor + "<br>"  for c in dc])
            return HttpResponse('{{ form.as_p }}')
#            return HttpResponseRedirect('/course/')
    else:
        form = CourseForm()

    return render(request,'add_course.html', {
        'form': form,
    })

# f = PatronForm(request.POST)
# if f.is_valid():
#     new_patron = f.save()
# def get_user_ecomaps():
# 	"""Return all ecomaps belonging to a particular user"""



# def get_course_ecomaps():
# 	"""Return all ecomaps belonging to a particular course"""


# def submit_feedback():
# 	"""Direct user to page to fill out feedback form."""


# def feedback_recieved():
#     """Shows confirmation that feedback user submitted was sent and offers links so that they may go to other areas of site."""

# def edit_course():
#     """Allows details of course to be altered."""


# def remove_student_from_course():
#     """Removes a student from the course."""



