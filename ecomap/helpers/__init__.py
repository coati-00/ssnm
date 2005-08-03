from ecomap.model import *
import formencode

def createTables():
    Ecouser.createTable(ifNotExists=True)
    Ecomap.createTable(ifNotExists=True)

def dropTables():
    Ecomap.dropTable(ifExists=True)
    Ecouser.dropTable(ifExists=True)

class EcomapSchema(formencode.Schema):
    name = validators.String(not_empty=True)
    description = validators.String()

def setup_for_tests():
    dropTables()
    createTables()

def teardown_tests():
    dropTables()
