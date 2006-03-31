from sqlobject import *
from turbogears.database import PackageHub
import ecomap.helpers
hub = PackageHub("quip")
__connection__ = hub

soClasses = ["Ecouser","Course","Ecomap"]

from mx import DateTime

class Ecouser(SQLObject):
    uni           = UnicodeCol(length=50)
    password      = UnicodeCol(length=50,default="")
    securityLevel = IntCol(default=2)
    firstname     = UnicodeCol(length=50)
    lastname      = UnicodeCol(length=50)
    ecomaps       = MultipleJoin('Ecomap')
    instructorOf  = MultipleJoin('Course')
    courses       = RelatedJoin('Course', joinColumn='student', otherColumn='course',intermediateTable='student_courses')

    def delete(self):
        for course in self.courses:
            course.removeEcouser(self.id)
        self.destroySelf()

    def toggle_admin(self):
        if self.securityLevel == 2:
            self.securityLevel = 1
        elif self.securityLevel == 1:
            self.securityLevel = 2

    def fullname(self):
        return self.firstname + " " + self.lastname

    def instructor_courses(self):
        """ returns courses that this user is the instructor of """
        return Course.select(Course.q.instructorID == self.id)

class Course(SQLObject):
    name        = UnicodeCol(length=50,default="")
    description = UnicodeCol(length=50,default="")
    instructor  = ForeignKey('Ecouser',cascade=True)
    ecomaps     = MultipleJoin('Ecomap')
    students    = RelatedJoin('Ecouser', joinColumn='course', otherColumn='student',intermediateTable='student_courses')

    def delete(self):
        for student in self.students:
            self.removeEcouser(student.id)
        self.destroySelf()

    def add_students(self,uni_list):
        invalid_ids = []
        # scan through user list to get users.  make sure they exist, then add to course
        for student_uni in uni_list:
            # don't add the student if he is the instructor of the course
            if student_uni == self.instructor.uni:
                continue
            
            this_user = Ecouser.select(Ecouser.q.uni == student_uni)
            # make sure this is a valid, existing user
            if this_user.count() == 1:
                if not this_user[0] in self.students:
                    self.addEcouser(this_user[0].id)
            else:
                # add this user to our list of users
                # make sure it is a valid UNI
                (firstname,lastname) = ecomap.helpers.ldap_lookup(student_uni)
                if firstname == "" and lastname == "":
                    # not in the ldap.  bad uni.  exit
                    invalid_ids.append(student_uni)
                else:
                    eus = EcouserSchema()
                    d = eus.to_python({'uni' : student_uni, 'securityLevel' : 2, 'firstname' : firstname, 'lastname' : lastname})
                    this_user = Ecouser(uni=d['uni'],securityLevel=d['securityLevel'],firstname=d['firstname'],lastname=d['lastname'])
                    if not this_user in self.students:
                        self.addEcouser(this_user.id)
        return invalid_ids

        


def get_all_courses():
    return list(Course.select(Course.q.instructorID == Ecouser.q.id, orderBy=['name']))


class Ecomap(SQLObject):
    name        = UnicodeCol(length=50)
    description = UnicodeCol(length=100,default='')
    created     = DateTimeCol(default=DateTime.now)
    modified    = DateTimeCol(default=DateTime.now)
    owner       = ForeignKey('Ecouser',cascade=True)
    course      = ForeignKey('Course',cascade=True)
    public      = BoolCol(default=False)
    flashData   = UnicodeCol(default='')

    def formatted_created(self):
        return self.created.strftime("%A, %B %d, %Y")

    def formatted_modified(self):
        return self.modified.strftime("%A, %B %d, %Y")

    def save(self,root):
        """ updates the ecomap based on a dom tree """

        name        = ecomap.helpers.safe_get_element_child(root,"name")
        description = ecomap.helpers.safe_get_element_child(root,"description")
        self.flashData = root.getElementsByTagName("flashData")[0].toxml()
        self.name = name
        self.description = description
        self.modified = DateTime.now()
        #want to check if this actually saves so i can REALLY return an OK
        #if it doesn't save, return NOT OK
        return "<data><response>OK</response></data>"
        
    def load(self,readonly="true"):
        return "<data><response>OK</response><isreadonly>" + readonly + "</isreadonly><name>" + \
               self.name + "</name><description>" + self.description + \
               "</description>" + self.flashData + "</data>"



    

