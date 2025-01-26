from src.utilities.definitions import *
from src.parking.parkingspot import *

class LargeSpot(ParkingSpot):
    def __init__(self, number):
        super().__init__(number, ParkingSpotType.LARGE)

