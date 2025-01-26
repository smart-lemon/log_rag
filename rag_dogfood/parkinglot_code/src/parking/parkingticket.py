from src.utilities.utils import *
from src.utilities.definitions import *


class ParkingTicket:
    def __init__(self):
        self.counter = 1
        self.ticket = 10

    def get_parking_ticket(self):
        log_message(self.__class__.__name__, __name__, f"Getting parking ticket {self.ticket}")
        self.ticket += self.counter
        return self.ticket
