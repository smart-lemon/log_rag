from src.utilities.utils import *
from src.utilities.definitions import *
import threading


class ParkingSpot(ABC):
    def __init__(self, number, parking_spot_type):
        self.__counter = 1
        self.__number = number
        self.__free = True
        self.__vehicle = None
        self.__parking_spot_type = parking_spot_type

    def is_free(self):
        log_message(self.__class__.__name__, __name__,
                    f"Parking spot {self.__number} is {self. self.__free}.")
        return self.__free

    def assign_vehicle(self, vehicle):
        self.__vehicle = vehicle
        log_message(self.__class__.__name__, __name__,
                    f"Parking spot {vehicle} assigned.")
        self.__free  = False

    def remove_vehicle(self):
        self.__vehicle = None
        log_message(self.__class__.__name__, __name__,
                  f"Parking spot {self.__vehicle} freed.")
        self.__free  = True

    def get_spot(self, number):
        self.__counter += 1
        self.__number = self.__counter + number
        log_message(self.__class__.__name__, __name__,
                    f"Parking get spot {self.__number} .")
        return self.__number

    def get_number(self):
        log_message(self.__class__.__name__, __name__,
                    f"Parking get number {self.__number} .")
        return self.__number