from sqlobject import *
import ecomap.config as config

__connection__ = config.param("dsn")

class Ecomap(SQLObject):
	name = UnicodeCol(length=50)
	description = UnicodeCol(length=100,default='')
	flashData = UnicodeCol(default='')
	

