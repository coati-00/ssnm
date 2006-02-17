from sqlobject import *
import ecomap.config as config

__connection__ = config.param("dsn")

from courseTable import Course
from ecouserTable import Ecouser
from ecomapTable import Ecomap
    

