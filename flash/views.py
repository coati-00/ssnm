# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import get_object_or_404, render_to_response
from xml.dom.minidom import parse, parseString
from intervention.models import *

blank_response_evil = """<data>
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
                <instruction>Step 1: Add person to \n             your map</instruction>
                <supportLevel>
                    <text>Somewhat Risky</text>
                    <color>0x7167f5</color>
                </supportLevel>
                <supportLevel>
                    <text>Risky</text>
                    <color>0xF30DF5</color>
                </supportLevel>
                <supportLevel>
                    <text>Very Risky</text>
                    <color>0xf50d3f</color>
                </supportLevel>
            </supportLevels>
            <supportTypes>
                <instruction>Step 2: Add types of risk</instruction>
                <supportType><text>Drugs</text></supportType>
                <supportType><text>Unsafe Sex</text></supportType>
                <supportType><text>Violence</text></supportType>
                </supportTypes>
            <persons></persons>
        </flashData>
        </data>"""
        
 
blank_response_good = """<data>
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


blank_responses = {"good": blank_response_good, "evil": blank_response_evil}

        
def display_good (request):
    return display (request, 'good')

def display_evil (request):
    return display (request, 'evil')
        
def display (request, map_label = 'good'):
    xml = blank_responses[ map_label ]
    testing = False
    if request.POST == {} and not testing:
        return  HttpResponse( "Nothing in request POST.")

    post = request.raw_post_data
    dom = parseString(post)
    action = dom.getElementsByTagName("action")[0].firstChild.toxml()
    if user_id != None:
        map_user = get_object_or_404(User, pk=user_id)
    else:
        map_user = request.user
    username = map_user.first_name
    
    if testing:
        action == "load"
    
    
    if action == "load":
        #pdb.set_trace()
        #print "load"             
        try:
            #print map_user.get_js_user_object ()
            obj = simplejson.loads(map_user.get_js_user_object ())
            xml = obj['games']['ssnm_game_state'][map_label]
            if xml == "":
                xml = blank_responses[ map_label ]
                return  HttpResponse(xml % username)
            else:
                return  HttpResponse(xml) #found map, return it verbatim.
        except (KeyError, ValueError):
            print "No map found"
            #print "key_error"                                                 
            xml = blank_responses[ map_label ] 
            return HttpResponse (xml % username)

            
    elif action == "save":
        print "save"
        if int(user_id) != request.user.id:
            print "Can't save someone else's map."
            return HttpResponse ("<data><response>OK</response></data>")
       
        name = dom.getElementsByTagName("name")[0].toxml()
        flash_data = dom.getElementsByTagName("flashData")[0].toxml()
        map_to_save = "<data><response>OK</response><isreadonly>false</isreadonly>%s%s</data>" % (name, flash_data)
        #pdb.set_trace()
            
        #edge case:
        if request.user.get_profile().js_user_object == '':
            request.user.get_profile().js_user_object = '{}'
            
        obj = simplejson.loads(request.user.get_js_user_object ())
        
        if 'games' not in obj:
            obj['games'] = {}
        if 'ssnm_game_state' not in obj['games']:
            obj['games']['ssnm_game_state'] = {}
        
        
        obj['games']['ssnm_game_state'][map_label] = map_to_save;
        
        #print map_to_save
        request.user.set_js_user_object (simplejson.dumps(obj));
        request.user.save()
        return HttpResponse ("<data><response>OK</response></data>")
        
        
    else:
        print "Problem."
        return  HttpResponse("<data><response>Problem</response></data>")



def ssnm_xml_to_python_obj_good (xml):
    return ssnm_xml_to_python_obj (xml, 'good')


def ssnm_xml_to_python_obj_evil (xml):
    return ssnm_xml_to_python_obj (xml, 'evil')



def ssnm_xml_to_python_obj (xml, map_type):
    #preliminaries
    
    from math import sqrt
    person_data_xml_tags =  ['name', 'x', 'y', 'supportLevel']
    circle_labels = ['inner circle', 'middle circle', 'outer circle', 'outside all circles']
    

    if map_type == 'good':
        support_level_labels = ['Not Very Helpful', 'Somewhat Helpful', 'Very Helpful']
    else:
        support_level_labels = ['Somewhat Risky', 'Risky', 'Very Risky']
    
    center_x = 145.0 # coordinates of the center of the circle wrt the top left edge of the map.
    center_y = 325.0
    person_rect_width  = 100.0
    person_rect_height = 50.0
    
    dom = parseString(xml)
    #circles:
    circle_sizes = [int(float(c.childNodes[0].data)) for c in dom.getElementsByTagName("radius")]
    
    #people:
    people_xml = dom.getElementsByTagName("persons")[0].childNodes
    extract_from_dom  = lambda x, y: x.getElementsByTagName(y)[0].childNodes[0].data
    people_data = []
    for p in people_xml:
        data = {}
        #basic:
        for k in person_data_xml_tags:
            try:
                data [k] = extract_from_dom (p, k)
            except:
                pass #no data, no problem
        #support_level:
        data['support_level_label'] = support_level_labels[ int(data['supportLevel'])]

        #support types:
        data['support_types'] = [s.childNodes[0].data for s in p.getElementsByTagName('support')]
                
        # which circle:
        if data['x'] and data['y']:
            offset_x = float(data['x']) - center_x + ( person_rect_width / 2 ) 
            offset_y = float(data['y']) - center_y + ( person_rect_height / 2 )
            dist  = sqrt(pow(offset_x, 2) + pow(offset_y, 2))
            n = len([r for r in circle_sizes if dist > r]) # how many circles the person is outside
            data ['circle_location']  = circle_labels[n]
        people_data.append(data)
    return people_data    
    
def test_file(request):
	#flash_data = open("media/flash/ecomap.swf", "rb").read()
	pwd = os.system("pwd")
	return HttpResponse(pwd)
	#return HttpResponse(flash_data, mimetype="application/x-shockwave-flash") #doesn't look like this works

def test_xml (request):
    return test_xml(request, 'good')
