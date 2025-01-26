# Import necessary modules
from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.parking.compactspot import *
from src.vehicle.vehicle_types import *
from src.mgmt.parking_attendant import *

if __name__ == "__main__":

    # Create a ParkingLot instance
    parking_lot = ParkingLot("Test Parking Lot", "123 Main Street")

    # Create a car object
    car = Car("ABC123")

    # Get a new parking ticket
    ticket = parking_lot.get_new_parking_ticket(car)

    # Simulate early exit
    car.get_license_number()

    # Close the ticket
    parking_lot.close_parking_ticket(ticket)

    # Mark the parking spot as free
    parking_lot.free_spot(car)

    attendent = ParkingAttendant("Thomas", "None", AccountStatus.ACTIVE)
    valid_ticket = attendent.process_ticket(car.get_ticket())

