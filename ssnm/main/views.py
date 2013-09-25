'''Each view renders page of site with the excection of
 display - that method deals with the flash in the web page.'''
from ssnm.main.models import Ecomap, CreateAccountForm
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth import login, logout
from xml.dom.minidom import parseString
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from registration.signals import user_registered


def display(request, map_id):
    '''Method processes infromation comunicated by flash.'''
    post = request.raw_post_data

    #  making sure there is something in the POST request
    if request.POST == {}:
        return HttpResponse("Nothing in request POST.")

    #  parse post request and get infromation
    dom = parseString(post)
    action = dom.getElementsByTagName("action")[0].firstChild.toxml()

    #  retrieve the appropriate map for the page
    ecomap = Ecomap.objects.get(pk=map_id)

    if action == "load":
        return HttpResponse(ecomap.ecomap_xml)  # return saved xml

    if action == "save":
        name = dom.getElementsByTagName("name")[0].toxml()
        flash_data = dom.getElementsByTagName("flashData")[0].toxml()
        #  get xml detailing the position of elements on the screen
        map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
        # add some extra data
        ecomap.ecomap_xml = map_to_save
        ecomap.save()
        return HttpResponse("<data><response>OK</response></data>")


def get_map_details(request, map_id):
    '''Make user enter name and description of the map'''
    user = request.user
    ecomap = Ecomap.objects.get(pk=map_id)
    if request.method == 'POST':  # If the form has been submitted...
        form = EcomapForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            ecomap.name = form.cleaned_data['name']
            ecomap.description = form.cleaned_data['description']
            ecomap.save()
            return render_to_response('thanks.html')
    else:
        form = EcomapForm()  # An unbound form

    return render(request, 'details.html', {  'form': form, 'map' : ecomap})


@login_required
def get_map(request, map_id=""):
    '''User has requested a save ecomap - retrieve it.'''
    user = request.user
    if map_id != "":
        ecomap = Ecomap.objects.get(pk=map_id)
        return render_to_response('game_test.html', {'map': ecomap})
    else:
        ecomap = Ecomap.objects.create_ecomap(owner=user)
        new_xml = """<data>
            <response>OK</response>
            <isreadonly>false</isreadonly>
            <name>%s</name>
            <flashData>
            <circles>
            <circle><radius>499</radius></circle>
            <circle><radius>350</radius></circle>
            <circle><radius>200</radius></circle>
            </circles>
            <supportLevels>
            <supportLevel><text>Very Helpful</text>
            </supportLevel>
            <supportLevel><text>Somewhat Helpful</text>
            </supportLevel>
            <supportLevel><text>Not So Helpful</text>
            </supportLevel>
            </supportLevels>
            <supportTypes>
            <supportType><text>Social</text></supportType>
            <supportType><text>Advice</text></supportType>
            <supportType><text>Empathy</text></supportType>
            <supportType><text>Practical</text></supportType>
            </supportTypes>
            <persons></persons>
            </flashData>
            </data>"""

        eco_xml = new_xml % request.user
        ecomap.ecomap_xml = eco_xml
        ecomap.save()

    return render_to_response('game_test.html', {'map' : ecomap})


@login_required
def show_maps(request):
    '''Show the user all of their saved maps.
    Allow user to click on one and have it retrieved.'''
    user_obj = User.objects.get(username=str(request.user))
    user_key = user_obj.pk
    maps = Ecomap.objects.filter(owner=user_obj)
    return render_to_response("map_page.html", {'maps': maps, 'user': user_obj, })


def logout(request):
    return HttpResponseRedirect('/accounts/logout/')


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True, widget=forms.Textarea)
    sender = forms.EmailField(required=True)


class EcomapForm(forms.Form):
    '''TO DO:Form to allow user to add additional data about their graph
     - user should be able to add description of map and give it a name.'''
    name = forms.CharField(max_length=50, label="Name")
    description = forms.CharField(max_length=500, widget=forms.Textarea, label="Description")


class LoginForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
    username = forms.CharField(max_length=50, required=True, label="Username")
    password = forms.CharField(max_length=50, required=True, label="Last Name")


# Done --> definately needs to be cleaned up
def contact(request):
    '''Contact someone regarding the project - WHO???'''
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['cdunlop@columbia.edu']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return render_to_response('thanks.html')
    else:
        form = ContactForm()  # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })


def thanks(request):
    """Returns thanks page."""
    return render_to_response('thanks.html')


def about(request):
    """Returns about page."""
    return render_to_response('about.html')


def help_page(request):
    """Returns help page."""
    return render_to_response('help.html')


def create_account(request):
    '''This is based off of django-request - creates a new user account.'''
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        try:
            User.objects.get(username=request.POST['username'])
            raise forms.ValidationError("this username already exists")
        except User.DoesNotExist:
            if 'password1' in request.POST and 'password2' in request.POST:
                print "comparing passwords"
                if request.POST['password1'] != request.POST['password2']:
                    raise forms.ValidationError("passwords dont match each other")

                if request.POST['password1'] == request.POST['password2']:
                    new_user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password1'])
                    new_user.first_name = request.POST['first_name']
                    new_user.last_name = request.POST['last_name']
                    new_user.save()
                    return HttpResponseRedirect('/thanks/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()  # An unbound form

    return render(request, 'create_account.html', {
        'form': form,
    })


def my_login(request):
    '''My login method -- probably very wrong...'''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        #print user.username
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/show_maps/')
            else:
                return HttpResponseRedirect('It appears you do not have an account, please create one to use this application')
        else:
            forms.ValidationError('This login is incorrect.')
    else:
        form = LoginForm()  # An unbound form

    return render(request, 'login.html', {
        'form': form,
    })


def delete_map(request, map_id):
    '''Deletes the selected map.'''
    ecomap = Ecomap.objects.get(pk=map_id)
    ecomap.delete()
    return show_maps(request)
