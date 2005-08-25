#!/usr/bin/env python

import sys
sys.path.append(".")
import ecomap.config as config

config.MODE = "regressiontest"

from ecomap.helpers import *

import unittest
import sys
import os
sys.path.append('test')

modules_to_test = (
    'TestEcouser',
    'TestEcomap',
    'TestController',
    
    )

TestRunner = unittest.TextTestRunner
allsuites = unittest.TestSuite()

tests = os.listdir(os.curdir + '/test')
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test in tests:
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        allsuites.addTest(m.test_suite())


#def suite():
#    alltests = unittest.TestSuite()
#    import pdb; pdb.set_trace()
#    for module in map(__import__, modules_to_test):
#        alltests.addTest(unittest.findTestCases(module))
#    return alltests

def setup_module(module):
    setup_for_tests()

def teardown_module(module):
    teardown_tests()

class TestMain:
    def test_one(self):
        assert 1 == 1


if __name__ == '__main__':

    # create the database for tests to run against, etc.
    dropTables()
    createTables()

#    createSettingTypes()
#    createTemplateTypes()
#    createDefaultSkin()
#    createDefaultConfiguration()
#    createQuestionTypes()
#    unittest.main(defaultTest='suite')
    TestRunner(verbosity=1).run(allsuites)

    dropTables()



