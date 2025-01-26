# Import necessary modules

from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.parking.compactspot import *
from src.vehicle.vehicle_types import *

if __name__ == "__main__":
    # Import necessary modules

    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Create an electric car object
    electric_car = ElectricCar("STU345")
    # Get a parking ticket
    ticket = parking_lot.get_new_parking_ticket(electric_car)
    # Find an available electric spot
    available_electric_spot = parking_lot.find_available_spot(ElectricSpot)
    # Check if there is a free electric spot
    if available_electric_spot:
        # Assign the electric car to the electric spot
        available_electric_spot.assign_vehicle(electric_car)
        # Mark the spot as occupied
        available_electric_spot.is_free = False
    else:
        # Find an available compact spot
        available_compact_spot = parking_lot.find_available_spot(CompactSpot)
        # Assign the electric car to the compact spot
        available_compact_spot.assign_vehicle(electric_car)
        # Mark the spot as occupied
        available_compact_spot.is_free = False
    # Print a confirmation message
