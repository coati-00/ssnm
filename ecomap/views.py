'''Each view renders page of site with the excection of
 display - that method deals with the flash in the web page.'''
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django import forms
from ecomap.models import Ecouser, Ecomap
from django.contrib.auth import login
from django.contrib.auth import logout
from xml.dom.minidom import parseString
#this code taken from nynja
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect


# This works but user can only create one map
# @login_required
# def display(request):
#     #import pdb
#     #pdb.set_trace()
#     new_xml = """<data>
#         <response>OK</response>
#         <isreadonly>false</isreadonly>
#         <name>%s</name>
#         <flashData>
#             <circles>
#                 <circle><radius>499</radius></circle>
#                 <circle><radius>350</radius></circle>
#                 <circle><radius>200</radius></circle>
#             </circles>
#             <supportLevels>
#                 <supportLevel><text>Very Helpful</text>
#                 </supportLevel>
#                 <supportLevel><text>Somewhat Helpful</text>
#                 </supportLevel>
#                 <supportLevel><text>Not So Helpful</text>
#                 </supportLevel>
#             </supportLevels>
#             <supportTypes>
#                 <supportType><text>Social</text></supportType>
#                 <supportType><text>Advice</text></supportType>
#                 <supportType><text>Empathy</text></supportType>
#                 <supportType><text>Practical</text></supportType>
#                 </supportTypes>
#             <persons></persons>
#         </flashData>
#         </data>"""
#     post = request.raw_post_data
#     dom = parseString(post)
#     action = dom.getElementsByTagName("action")[0].firstChild.toxml()
#     user = request.user
#     username = user.first_name
#     ecouser = user.get_profile()
#     m_xml = ""
#     count_maps = ecouser.ecomap_set.count()
#     if count_maps > 0:
#         find_map = ecouser.ecomap_set.all()
#         for m in find_map:
#             m_xml = m.ecomap_xml
#     if action == "load":
#         if count_maps == 0:
#            return HttpResponse(new_xml % username)
#         else:
#             return HttpResponse(m_xml)
#     if action == "save":
#         name = dom.getElementsByTagName("name")[0].toxml()
#         flash_data = dom.getElementsByTagName("flashData")[0].toxml()
#         map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
#         current_user = user.get_profile()
#         new_map = Ecomap(ecomap_xml=map_to_save, title="title", owner=current_user)
#         new_map.save()
# #         return HttpResponse ("<data><response>OK</response></data>")
# def game(request):
#     return render_to_response('ecomap/game_test.html')


@login_required
def display(request, map_id=""):
    '''This method deals with the flash inside the web page,
     it passes it the needed data as xml in a large string'''
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
    if request.POST == {}:
        return HttpResponse("Nothing in request POST.")
    post = request.raw_post_data
    dom = parseString(post)
    action = dom.getElementsByTagName("action")[0].firstChild.toxml()
    user = request.user
    username = user.first_name
    ecouser = user.get_profile()
    m_xml = ""

    if action == "load":
        if map_id == "":
            return HttpResponse(new_xml % username)
            # this runs correctly - if use has no map they create new one
        else:
            find_map = ecouser.ecomap_set.get(pk=map_id)
            m_xml = find_map.ecomap_xml
            return HttpResponse(m_xml)

    if action == "save":
        name = dom.getElementsByTagName("name")[0].toxml()
        flash_data = dom.getElementsByTagName("flashData")[0].toxml()
        map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
        current_user = user.get_profile()
        new_map = Ecomap(ecomap_xml=map_to_save, name="some_map_name", owner=current_user)
        new_map.save()
        return HttpResponse("<data><response>OK</response></data>")


@login_required
def ecomap(request):
    '''User would like to create an ecomap - redirect them to a blank one.'''
    return render_to_response('ecomap/game_test.html')


@login_required
def get_map(request, map_id=""):
    '''User has requested a save ecomap - retrieve it.'''
    print map_id
    ecomap = Ecomap.objects.get(pk=map_id)
    print ecomap
    return render_to_response('ecomap/game_test.html', {'map': ecomap})


@login_required
def show_maps(request):
    '''Show the user all of their saved maps.
    Allow user to click on one and have it retrieved.'''
    user = request.user
    ecouser = request.user.get_profile()
    maps = ecouser.ecomap_set.all()
    return render_to_response("ecomap/map_page.html", {'maps': maps, 'user': user, })


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100)
    message = forms.CharField(max_length=200)
    sender = forms.EmailField()


class FeedbackForm(forms.Form):
    '''This is a form class that will be returned later in the contact
    form view. CAN PROB DELETE ONE JUST HAVE ONE FORM'''
    subject = forms.CharField(max_length=100)
    message = forms.CharField(max_length=200)
    sender = forms.EmailField()


class EcomapForm(forms.Form):
    '''TO DO:Form to allow user to add additional data about their graph
     - user should be able to add description of map and give it a name.'''
    name = forms.CharField(max_length=50)


def logout(request):
    '''Allow user to log out.'''
    logout(request)
    return HttpResponse("You have successfully logged out.")


def guest_login(self, uni="", password=""):  # hows guest login page
    """Presents login page for guest NOT SURE IF THIS SHOULD
    BE DIFFERNENT FROM THE REGULAR
    LOGIN PAGE - HAVE ONE PAGE WITH OPTION TO CREATE ACCOUNT."""
    return render_to_response("ecomap/guest_login.html")


# Done --> definately needs to be cleaned up
def contact(request):
    '''Contact someone regarding the project - WHO???'''
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['someone@somewhere.com']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return render_to_response('ecomap/thanks.html')
    else:
        form = ContactForm()  # An unbound form

    return render(request, 'ecomap/contact.html', {
        'form': form,
    })


def about(request):
    """Returns about page."""
    return render_to_response('ecomap/about.html')


def help_page(request):
    """Returns help page."""
    return render_to_response('ecomap/help.html')
