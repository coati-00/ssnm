from ecomap.model import *
import formencode

def createTables():
    Application.createTable(ifNotExists=True)
    Push.createTable(ifNotExists=True)
    Log.createTable(ifNotExists=True)

def dropTables():
    Application.dropTable(ifExists=True)
    Push.dropTable(ifExists=True)
    Log.dropTable(ifExists=True)

class ApplicationSchema(formencode.Schema):
    name    = validators.String(not_empty=True)
    pmt_pid = validators.Int()
    svn_url = validators.String(not_empty=True)


