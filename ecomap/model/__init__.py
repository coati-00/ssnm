from sqlobject import *
import ecomap.config as config

__connection__ = config.param("dsn")

from ecouserTable import Ecouser
from ecomapTable import Ecomap
    

