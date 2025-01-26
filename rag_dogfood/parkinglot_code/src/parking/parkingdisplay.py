from src.utilities.utils import *
from src.utilities.definitions import *


class ParkingDisplayBoard:
    def __init__(self, id):
        self.__id = id
        self.__handicapped_free_spot = None
        self.__compact_free_spot = None
        self.__large_free_spot = None
        self.__motorbike_free_spot = None
        self.__electric_free_spot = None

    def show_empty_spot_number(self):
        message = ""
        if self.__handicapped_free_spot.is_free():
            log_message(self.__class__.__name__, __name__,
                        f"Free Handicapped {self.__handicapped_free_spot.get_number()}")
            message += "Free Handicapped: " + self.__handicapped_free_spot.get_number()
        else:
            message += "Handicapped is full"
            log_message(self.__class__.__name__, __name__,
                        f"Handicapped is full {self.__handicapped_free_spot.get_number()}")

        message += "\n"

        if self.__compact_free_spot.is_free():
            log_message(self.__class__.__name__, __name__,
                        f"Free Compact: {self.__compact_free_spot.get_number()}")
            message += "Free Compact: " + self.__compact_free_spot.get_number()
        else:
            message += "Compact is full"
        message += "\n"

        if self.__large_free_spot.is_free():
            log_message(self.__class__.__name__, __name__,
                        f"Free Large: {self.__large_free_spot.get_number()}")
            message += "Free Large: " + self.__large_free_spot.get_number()
        else:
            log_message(self.__class__.__name__, __name__,
                      f"Large is full {self.__large_free_spot.get_number()}")
            message += "Large is full"

        message += "\n"

        if self.__motorbike_free_spot.is_free():
            log_message(self.__class__.__name__, __name__,
                      f"Free Motorbike:l {self.__motorbike_free_spot.get_number()}")
            message += "Free Motorbike: " + self.__motorbike_free_spot.get_number()
        else:
            log_message(self.__class__.__name__, __name__,
                      f"Motorbike is full {self.__motorbike_free_spot.get_number()}")
            message += "Motorbike is full"
        message += "\n"

        if self.__electric_free_spot.is_free():
            log_message(self.__class__.__name__, __name__,
                      f"Free Electric: {self.__electric_free_spot.get_number()}")
            message += "Free Electric: " + self.__electric_free_spot.get_number()
        else:
            message += "Electric is full"

        return message
