from abc import ABC, abstractmethod
from src.utilities.utils import *
from src.utilities.definitions import *

class Vehicle(ABC):
    def __init__(self, license_number, vehicle_type, ticket=None):
        self.__license_number = license_number
        self.__type = vehicle_type
        self.__ticket = ticket

    def assign_ticket(self, ticket):
        log_message(self.__class__.__name__, __name__, f"Assigning ticket {self.__ticket}")
        self.__ticket = ticket

    def remove_ticket(self):
        log_message(self.__class__.__name__, __name__, f"Deleting ticket {self.__ticket}")
        self.__ticket = None

    def get_ticket(self):
        log_message(self.__class__.__name__, __name__, f"Returning ticket {self.__ticket}")
        return self.__ticket

    def get_type(self):
        log_message(self.__class__.__name__, __name__, f"Car type is {self.__type}")
        return self.__type

    def get_license_number(self):
        log_message(self.__class__.__name__, __name__, f"License is {self.__license_number}")
        return self.__type

class Car(Vehicle):
    def __init__(self, license_number, ticket=None):
        super().__init__(license_number, VehicleType.CAR, ticket)


class Van(Vehicle):
    def __init__(self, license_number, ticket=None):
        super().__init__(license_number, VehicleType.VAN, ticket)


class Truck(Vehicle):
    def __init__(self, license_number, ticket=None):
        super().__init__(license_number, VehicleType.TRUCK, ticket)


class MotorBike(Vehicle):
    def __init__(self, license_number, ticket=None):
        super().__init__(license_number, VehicleType.MOTORBIKE, ticket)

class ElectricCar(Vehicle):
    def __init__(self, license_number, ticket=None):
        super().__init__(license_number, VehicleType.ELECTRIC, ticket)