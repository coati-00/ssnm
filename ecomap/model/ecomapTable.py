from sqlobject import *
import ecomap.config as config
__connection__ = config.param('dsn')

# from ecomap.model import __connection__
from mx import DateTime

class Ecomap(SQLObject):
    name = UnicodeCol(length=50)
    description = UnicodeCol(length=100,default='')
    created = DateTimeCol(default=DateTime.now)
    modified = DateTimeCol(default=DateTime.now)
    owner = ForeignKey('Ecouser',cascade=True)
    public = BoolCol(default=False)
    flashData = UnicodeCol(default='')
