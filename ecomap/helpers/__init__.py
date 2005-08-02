from ecomap.model import *
import formencode

def createTables():
    Ecomap.createTable(ifNotExists=True)

def dropTables():
    Ecomap.dropTable(ifExists=True)

class ApplicationSchema(formencode.Schema):
    name    = validators.String(not_empty=True)
    pmt_pid = validators.Int()
    svn_url = validators.String(not_empty=True)

def setup_for_tests():
    dropTables()
    createTables()

def teardown_tests():
    dropTables()
