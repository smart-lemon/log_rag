from src.utilities.definitions import *
from src.parking.parkingspot import *

class ElectricSpot(ParkingSpot):
    def __init__(self, number):
        super().__init__(number, ParkingSpotType.ELECTRIC)