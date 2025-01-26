from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.parking.compactspot import *
from src.vehicle.vehicle_types import *
from src.mgmt.parking_attendant import *

if __name__ == "__main__":

    # Import necessary modules

    # Create a ParkingLot instance
    parking_lot = ParkingLot("Test Parking Lot", "123 Main Street")

    # Create a list of cars
    cars = [Car("ABC123"), Car("DEF456"), Car("GHI789")]

    # Park the cars
    for car in cars:
        ticket = parking_lot.get_new_parking_ticket(car)
        car.get_license_number()

    # Simulate cars leaving the parking lot at different times
    for car in cars:
        car.remove_ticket()
        parking_lot.free_spot(car)
        car.get_license_number()
