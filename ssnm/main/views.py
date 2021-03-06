'''Each view renders page of site with the excection of
 display - that method deals with the flash in the web page.'''
from xml.dom.minidom import parseString

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ssnm.main.models import Ecomap


@login_required
def display(request, map_id):
    '''Method processes information communicated by flash.'''
    post = request.body
    if request.POST == {}:
        return HttpResponse("Nothing in request POST.")

    #  parse post request and get information
    dom = parseString(post)
    action = dom.getElementsByTagName("action")[0].firstChild.toxml()
    ecomap = Ecomap.objects.get(pk=map_id)

    if action == "load":
        return HttpResponse(ecomap.ecomap_xml)  # return saved xml

    if action == "save":
        name = dom.getElementsByTagName("name")[0].toxml()
        flash_data = dom.getElementsByTagName("flashData")[0].toxml()
        map_to_save = ("<data><response>OK</response><isreadonly>false"
                       "</isreadonly>%s%s</data>" % (name, flash_data))
        ecomap.ecomap_xml = map_to_save
        ecomap.save()
        return HttpResponse("<data><response>OK</response></data>")


@login_required
def get_map(request, map_id):
    '''User has requested a saved ecomap - retrieve it.'''
    ecomap = Ecomap.objects.get(pk=map_id)
    return render(request, 'game_test.html', {'map': ecomap})


def handle_valid_map_details_form(form, ecomap, old_name):
    ecomap.name = form.cleaned_data['name']
    old_xml = ecomap.ecomap_xml
    new_xml = old_xml.replace(
        "<name>" + old_name + "</name>",
        "<name>" + form.cleaned_data['name'] + "</name>")
    ecomap.ecomap_xml = new_xml
    ecomap.description = form.cleaned_data['description']
    if ecomap.name != '':
        ecomap.save()
    return HttpResponseRedirect('/ecomap/' + str(ecomap.pk))


NEW_ECOMAP_XML = """<data>
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


@login_required
def get_map_details(request, map_id=""):
    '''Make user enter name and description of the map before
    letting them go to the actual map site'''
    user = request.user
    if map_id != "" and request.method == 'POST':
        ecomap = Ecomap.objects.get(owner=user, pk=map_id)
        old_name = ecomap.name
        form = EcomapForm(request.POST)
        if form.is_valid():
            return handle_valid_map_details_form(form, ecomap, old_name)

    elif request.method == 'POST':
        ecomap = Ecomap.objects.create_ecomap(owner=user)
        map_id = ecomap.pk
        new_xml = NEW_ECOMAP_XML

        form = EcomapForm(request.POST)
        if form.is_valid():
            ecomap.name = form.cleaned_data['name']
            ecomap.description = form.cleaned_data['description']
            eco_xml = new_xml % ecomap.name
            ecomap.ecomap_xml = eco_xml
            if ecomap.name != '':
                ecomap.save()
            return HttpResponseRedirect('/ecomap/' + str(ecomap.pk))

        elif request.POST['name'] == "":
            ecomap.delete()

    elif map_id != "":
        '''This is to fill in the form when it is retrieved for editing.'''
        ecomap = Ecomap.objects.get(pk=map_id)
        form = EcomapForm({"name": ecomap.name,
                           "description": ecomap.description})
    else:
        form = EcomapForm()
    return render(request, 'details.html', {'form': form})


@login_required
def show_maps(request):
    '''Show the user all of their saved maps.
    Allow user to click on one and have it retrieved.'''
    user_obj = User.objects.get(username=str(request.user))
    maps = Ecomap.objects.filter(owner=user_obj)
    return render(request, "map_page.html",
                  {'maps': maps, 'user': user_obj, })


@login_required
def go_home(request, map_id):
    '''Enable back to maps functionality in flash.'''
    user_obj = User.objects.get(username=str(request.user))
    maps = Ecomap.objects.filter(owner=user_obj)
    return render(
        request,
        "map_page.html",
        {'maps': maps, 'user': user_obj, })


@login_required
def logout(request):
    return HttpResponseRedirect('/accounts/logout/')


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
    sender = forms.EmailField(required=True)


class EcomapForm(forms.Form):
    '''TO DO:Form to allow user to add additional data about their graph
     - user should be able to add description of map and give it a name.'''
    name = forms.CharField(max_length=50, label="Name", required=True)
    description = forms.CharField(max_length=500, widget=forms.Textarea,
                                  label="Description", required=False)


class LoginForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
    username = forms.CharField(max_length=50, required=True, label="Username")
    password = forms.CharField(max_length=50, required=True, label="Last Name")


def contact(request):
    '''Contact someone regarding the project'''
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['cdunlop@columbia.edu']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            HttpResponseRedirect('/thanks/')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {
        'form': form,
    })


def delete_map(request, map_id):
    '''Deletes the selected map.'''
    ecomap = Ecomap.objects.get(pk=map_id)
    ecomap.delete()
    # return show_maps(request)
    return HttpResponseRedirect('/')
