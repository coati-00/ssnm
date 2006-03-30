from sqlobject import *
from turbogears.database import PackageHub
hub = PackageHub("quip")
__connection__ = hub

soClasses = ["Ecouser","Course","Ecomap"]

from mx import DateTime

class Ecouser(SQLObject):
    uni = UnicodeCol(length=50)
    password = UnicodeCol(length=50,default="")
    securityLevel = IntCol(default=2)
    firstname = UnicodeCol(length=50)
    lastname = UnicodeCol(length=50)
    ecomaps = MultipleJoin('Ecomap')
    instructorOf = MultipleJoin('Course')
    courses = RelatedJoin('Course', joinColumn='student', otherColumn='course',intermediateTable='student_courses')

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


class Course(SQLObject):
    name = UnicodeCol(length=50,default="")
    description = UnicodeCol(length=50,default="")
    instructor = ForeignKey('Ecouser',cascade=True)
    ecomaps = MultipleJoin('Ecomap')
    students = RelatedJoin('Ecouser', joinColumn='course', otherColumn='student',intermediateTable='student_courses')


class Ecomap(SQLObject):
    name = UnicodeCol(length=50)
    description = UnicodeCol(length=100,default='')
    created = DateTimeCol(default=DateTime.now)
    modified = DateTimeCol(default=DateTime.now)
    owner = ForeignKey('Ecouser',cascade=True)
    course = ForeignKey('Course',cascade=True)
    public = BoolCol(default=False)
    flashData = UnicodeCol(default='')

    

