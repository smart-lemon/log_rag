from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.parking.compactspot import *
from src.vehicle.vehicle_types import *
from src.mgmt.parking_attendant import *

if __name__ == "__main__":
    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Create a car object
    car = Car("ABC123")
    # Get a parking ticket
    ticket = parking_lot.get_new_parking_ticket(car)
    # Find an available compact spot
    available_spot = parking_lot.find_available_spot(CompactSpot)
    # Assign the car to the spot
    available_spot.assign_vehicle(car)
    # Mark the spot as occupied
    available_spot.is_free = False
