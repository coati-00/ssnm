from sqlobject import *
import ecomap.config as config
__connection__ = config.param('dsn')

# from ecomap.model import __connection__
from mx import DateTime

class Ecouser(SQLObject):
    uni = UnicodeCol(length=50)
    password = UnicodeCol(length=50,default="")
    firstname = UnicodeCol(length=50)
    lastname = UnicodeCol(length=50)
    ecomaps = MultipleJoin('Ecomap')
    instructorOf = MultipleJoin('Course')
    courses = RelatedJoin('Course', joinColumn='student', otherColumn='course',intermediateTable='student_courses')

    