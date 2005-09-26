from ecomap.model import *
import formencode
from formencode import validators

def createTables():
	Ecouser.createTable(ifNotExists=True)
	Ecomap.createTable(ifNotExists=True)

def dropTables():
	Ecomap.dropTable(ifExists=True)
	Ecouser.dropTable(ifExists=True)

class EcomapSchema(formencode.Schema):
	name		= validators.String(not_empty=True)
	description = validators.String()
	owner		= validators.Int()

class EcouserSchema(formencode.Schema):
	uni			= validators.String(not_empty=True)
	firstname	= validators.String()
	lastname	= validators.String()

def setup_for_tests():
	dropTables()
	createTables()

def teardown_tests():
	dropTables()


#This function can be dropped right into place and used
def validate_wind_ticket(ticketid):
	"""
	checks a wind ticketid.
	if successful, it returns (1,username,groups)
	otherwise it returns (0,error message)
	"""
	
	if ticketid == "":
		return (0,'no ticketid')
	uri = "https://wind.columbia.edu/validate?ticketid=%s" % ticketid
	import urllib
	response = urllib.urlopen(uri).read()
	lines = response.split("\n")
	if lines[0] == "yes":
		username = lines[1]
		groups = [line for line in lines[1:] if line != ""]
		return (1,username,groups)
	elif lines[0] == "no":
		return (0,"the ticket was already used or was invalid",[])
	else:
		return (0,"WIND did not return a valid response",[])

		
#This function needs to be linked to the data model
#LDAP lookup section can be used as is ** :)
def get_or_create_user(username,firstname="",lastname=""):

	import pdb; pdb.set_trace()

	""" if the user is already in the system, it returns the user object.
	otherwise, it creates a new one and returns that. the function has the
	side effect of putting the user into any class that wind says they
	should be a part of if they aren't already in it. """
	res = Ecouser.select(Ecouser.q.uni == username)

	if res.count() > 0:
		# found the user. 
		u = res[0]
		cherrypy.session['fullname'] = u.firstname + " " + u.lastname
		return u
	
	else:
		#this user doesn't exist in our DB yet.  Get details from LDAP if possible
		try:
			import ldap
			LDAP_SERVER = "ldap.columbia.edu"
			BASE_DN = "o=Columbia University, c=us"
			l = ldap.open(LDAP_SERVER)
			baseDN = BASE_DN
			searchScope = ldap.SCOPE_SUBTREE
			retrieveAttributes = None
			searchFilter = "uni=*%s" % username
			ldap_result_id = l.search(baseDN, searchScope, searchFilter,
					retrieveAttributes)
			result_set = []
			while 1:
				result_type, result_data = l.result(ldap_result_id, 0)
				if result_data == []:
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						values = result_data[0][1]
						for k, v in values.items():
							if k == 'sn':
								lastname = v[0]
							if k == 'givenname':
								firstname = v[0]
		except ImportError:
			# no ldap library
			pass
				
		if lastname == "":
			lastname = username

		cherrypy.session['fullname'] = firstname + " " + lastname

		eus = EcouserSchema()
		d = eus.to_python({'uni' : username, 'firstname' : firstname, 'lastname' : lastname})
		u = Ecouser(uni=d['uni'],firstname=d['firstname'],lastname=d['lastname'])

		return u
