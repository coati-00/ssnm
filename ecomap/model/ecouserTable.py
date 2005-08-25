from sqlobject import *
import ecomap.config as config
__connection__ = config.param('dsn')

# from ecomap.model import __connection__
from mx import DateTime

class Ecouser(SQLObject):
	uni = UnicodeCol(length=50)
	firstname = UnicodeCol(length=50)
	lastname = UnicodeCol(length=50)
	ecomaps = MultipleJoin('Ecomap')