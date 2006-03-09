from sqlobject import *
import ecomap.config as config

soClasses = ["Ecouser","Course","Ecomap"]

__connection__ = config.param("dsn")

from mx import DateTime

class Ecouser(SQLObject):
    uni = UnicodeCol(length=50)
    password = UnicodeCol(length=50,default="")
    securityLevel = IntCol()
    firstname = UnicodeCol(length=50)
    lastname = UnicodeCol(length=50)
    ecomaps = MultipleJoin('Ecomap')
    instructorOf = MultipleJoin('Course')
    courses = RelatedJoin('Course', joinColumn='student', otherColumn='course',intermediateTable='student_courses')


class Course(SQLObject):
    name = UnicodeCol(length=50)
    description = UnicodeCol(length=50)
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

    

