from sqlobject import *
import ecomap.config as config

__connection__ = config.param("dsn")

from ecomapTable import Ecomap
from ecouserTable import EcoUser
	

