from src.utilities.utils import *
from src.utilities.definitions import *

class ParkingRate:
    def __init__(self):
        self.rate = 10

    def get_parking_rate(self):
        log_message(self.__class__.__name__, __name__, f"The parking rate is {self.rate}")
        return self.rate