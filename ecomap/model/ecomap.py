from sqlobject import *
from ecomap.model import __connection__
from mx import DateTime

class Ecomap(SQLObject):
	name = UnicodeCol(length=50)
	description = UnicodeCol(length=100,default='')
	created = DateTimeCol(default=DateTime.now)
	modified = DateTimeCol(default=DateTime.now)
	owner = ForeignKey('EcoUser',cascade=True)
	public = BoolCol()
	flashData = UnicodeCol(default='')
	