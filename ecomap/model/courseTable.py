from sqlobject import *
import ecomap.config as config
__connection__ = config.param('dsn')

# from ecomap.model import __connection__
from mx import DateTime

class Course(SQLObject):
    instructor = ForeignKey('Ecouser',cascade=True)
    description = UnicodeCol(length=50)
    ecomaps = MultipleJoin('Ecomap')
    students = RelatedJoin('Ecouser', joinColumn='course', otherColumn='student',intermediateTable='student_courses')
    
