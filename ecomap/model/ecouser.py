from sqlobject import *
from ecomap.model import __connection__
from mx import DateTime

class EcoUser(SQLObject):
	UNI = UnicodeCol(length=50)
	name = UnicodeCol(length=100)
	ecomaps = MultipleJoin('Ecomap')	