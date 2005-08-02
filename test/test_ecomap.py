import sys
sys.path.append(".")
import ecomap.config
ecomap.config.MODE = "regressiontest"
from ecomap.helpers import *

def setup_module(module):
    setup_for_tests()

def teardown_module(module):
    teardown_tests()

class TestEcomap:
    def setup_class(self):
        self.map = Ecomap(name="test",description="test",flashData="blah blah blah")

    def teardown_class(self):
        self.map.destroySelf()

    def test_basics(self):
        assert self.map.name == "test"
        assert self.map.description == "test"
        assert self.map.flashData == "blah blah blah"
