from sqlobject import *
__connection__ = "postgres://keldridge@/ecomap"

class Ecomap(SQLObject):
	name = UnicodeCol(length=50)
	description = UnicodeCol(length=100,default='')
	flashData = UnicodeCol(default='')
	

