from sqlobject import *
import ecomap.config as config

__connection__ = config.param("dsn")

from ecomap import Ecomap
from ecouser import EcoUser
	

