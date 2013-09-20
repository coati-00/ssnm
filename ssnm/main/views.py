'''Each view renders page of site with the excection of
 display - that method deals with the flash in the web page.'''
from ssnm.main.models import Ecomap, EcomapManager
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

# @login_required
# def display(request):
#     print "inside display method"
#     '''This method deals with the flash inside the web page,
#     it passes it the needed data as xml in a large string'''
#     new_xml = """<data>
#         <response>OK</response>
#         <isreadonly>false</isreadonly>
#         <name>%s</name>
#         <flashData>
#             <circles>
#             <circle><radius>499</radius></circle>
#             <circle><radius>350</radius></circle>
#             <circle><radius>200</radius></circle>
#             </circles>
#             <supportLevels>
#             <supportLevel><text>Very Helpful</text>
#             </supportLevel>
#             <supportLevel><text>Somewhat Helpful</text>
#             </supportLevel>
#             <supportLevel><text>Not So Helpful</text>
#             </supportLevel>
#         </supportLevels>
#         <supportTypes>
#             <supportType><text>Social</text></supportType>
#             <supportType><text>Advice</text></supportType>
#             <supportType><text>Empathy</text></supportType>
#             <supportType><text>Practical</text></supportType>
#             </supportTypes>
#         <persons></persons>
#         </flashData>
#         </data>"""
#     #if request.POST == {}:
#     #    return HttpResponse("Nothing in request POST.")
#     post = request.raw_post_data
#     dom = parseString(post)
#     action = dom.getElementsByTagName("action")[0].firstChild.toxml()
#     user = request.user
#     username = user.first_name
#     #m_xml = ""

#     if action == "load":
#         if map_id == "":
#             return HttpResponse(new_xml % username)
#     #    else:
#     #        find_map = user.ecomap_set.get(pk=map_id)
#     #        m_xml = find_map.ecomap_xml
#     #        return HttpResponse(m_xml)

#     #if action == "save":
#     #    name = dom.getElementsByTagName("name")[0].toxml()
#     #    flash_data = dom.getElementsByTagName("flashData")[0].toxml()
#     #    map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
#     #    new_map = Ecomap(ecomap_xml=map_to_save, name="some_map_name", owner=user)
#     #    new_map.save()
#     #    return HttpResponse("<data><response>OK</response></data>")










def display(request, map_id):
    print "inside display method"
    '''This method deals with the flash inside the web page,
    it passes it the needed data as xml in a large string'''
    # new_xml = """<data>
    #     <response>OK</response>
    #     <isreadonly>false</isreadonly>
    #     <name>%s</name>
    #     <flashData>
    #         <circles>
    #         <circle><radius>499</radius></circle>
    #         <circle><radius>350</radius></circle>
    #         <circle><radius>200</radius></circle>
    #         </circles>
    #         <supportLevels>
    #         <supportLevel><text>Very Helpful</text>
    #         </supportLevel>
    #         <supportLevel><text>Somewhat Helpful</text>
    #         </supportLevel>
    #         <supportLevel><text>Not So Helpful</text>
    #         </supportLevel>
    #     </supportLevels>
    #     <supportTypes>
    #         <supportType><text>Social</text></supportType>
    #         <supportType><text>Advice</text></supportType>
    #         <supportType><text>Empathy</text></supportType>
    #         <supportType><text>Practical</text></supportType>
    #         </supportTypes>
    #     <persons></persons>
    #     </flashData>
    #     </data>"""

    post = request.raw_post_data
    print post
    if request.POST == {}:
        return HttpResponse("Nothing in request POST.")
    dom = parseString(post)
    print dom
    action = dom.getElementsByTagName("action")[0].firstChild.toxml()
    #user = request.user
    #print user
    #username = user.first_name
    #print "username inside display " + username
    ecomap = Ecomap.objects.get(pk=map_id)
    if action == "load":
        return HttpResponse(ecomap.ecomap_xml)
    if action == "save":
       name = dom.getElementsByTagName("name")[0].toxml()
       flash_data = dom.getElementsByTagName("flashData")[0].toxml()
       map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
       #new_map = Ecomap(ecomap_xml=map_to_save, name="some_map_name", owner=user)
       #new_map.save()
       ecomap.ecomap_xml = map_to_save
       ecomap.save()
       return HttpResponse("<data><response>OK</response></data>")

@login_required
def get_map(request, map_id=""):
    '''User has requested a save ecomap - retrieve it.'''
    user = request.user
    count_maps = user.ecomap_set.count()
    if count_maps > 0 and map_id != "":
        ecomap = Ecomap.objects.get(pk=map_id)
        print "inside retrieving map id" + str(map_id)
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

        print "new_xml is : " + new_xml + "\n\n"
        eco_xml = new_xml % username
        print "eco_xml with name substitute : " + new_xml + "\n\n"
        ecomap.ecomap_xml = eco_xml
        ecomap.save()
        print "ecomap.owner.first_name" + ecomap.owner.first_name
        print "ecomap.pk" + str(ecomap.pk)
        return render_to_response('game_test.html', {'map': ecomap})

    #         return HttpResponseNotFound('<h1>Page not found</h1>')
    # else:
    #     return HttpResponse('Unauthorized', status=401)


@login_required
def show_maps(request):
    '''Show the user all of their saved maps.
    Allow user to click on one and have it retrieved.'''
    user = request.user
    maps = user.ecomap_set.all()
    return render_to_response("map_page.html", {'maps': maps, 'user': user, })


def logout(request):
    return HttpResponseRedirect('/accounts/logout/')


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100)
    message = forms.CharField(max_length=200)
    sender = forms.EmailField()


class EcomapForm(forms.Form):
    '''TO DO:Form to allow user to add additional data about their graph
     - user should be able to add description of map and give it a name.'''
    name = forms.CharField(max_length=50)


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
            recipients = ['someone@somewhere.com']
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
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid(): #  now is valid
            try:
                print "inside try block"
                User.objects.get(username=form.cleaned_data['username']) #  checking to see if user exists
                raise forms.ValidationError("this username already exists")
            except User.DoesNotExist:
                print "inside except block, returning user name"
                #return form.cleaned_data['username']
            
                print "we have gotten past exception land"

                if 'password1' in form.cleaned_data and 'password2' in form.cleaned_data:
                    #make sure the passwords entered match
                    print "comparing passwords"
                    print form.cleaned_data['password1']
                    print form.cleaned_data['password2']
                    if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                        raise forms.ValidationError("passwords dont match each other")
                    if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                        new_user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
                        new_user.first_name = form.cleaned_data['firstname']
                        new_user.last_name = form.cleaned_data['lastname']
                        new_user.save()
                        return HttpResponseRedirect('thanks.html')

                else:
                    raise forms.ValidationError("You must enter two matching passwords")
                
    else:
        form = CreateAccountForm()  # An unbound form

    return render(request, 'create_account.html', {
        'form': form,
    })


def register(request):
    return render_to_response('registration.html')

def home(request):
    return render_to_response('home_page.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid(): #  now is valid
            username=form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/show_maps/')
                else:
                    return HttpResponseRedirect('It appears you do not have an account, please create one to use this application')
            else:
                forms.ValidationError('It appears you do not have an account, please create one to use this application')
    else:
        form = LoginForm()  # An unbound form

    return render(request, 'login.html', {
        'form': form,
    })
def delete_map(request, map_id):
    ecomap = Ecomap.objects.get(pk=map_id)
    ecomap.delete()




