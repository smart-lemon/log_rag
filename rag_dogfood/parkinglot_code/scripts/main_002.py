# Import necessary modules
from src.parking.parkinglot import ParkingLot
from src.parking.largespot import *
from src.vehicle.vehicle_types import *

if __name__ == "__main__":
    # Import necessary modules

    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Create a truck object
    truck = Truck("XYZ456")
    # Get a parking ticket
    ticket = parking_lot.get_new_parking_ticket(truck)
    # Find an available large spot
    available_spot = parking_lot.find_available_spot(LargeSpot)
    # Assign the truck to the spot
    available_spot.assign_vehicle(truck)
    # Mark the spot as occupied
    available_spot.is_free = False