# Import necessary modules
# Import necessary modules
from src.parking.parkinglot import ParkingLot
from src.parking.motobikespot import *
from src.vehicle.vehicle_types import *
if __name__ == "__main__":


    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Create a motorbike object
    motorbike = MotorBike("LMN789")
    # Get a parking ticket
    ticket = parking_lot.get_new_parking_ticket(motorbike)
    # Find an available motorbike spot
    available_spot = parking_lot.find_available_spot(MotorbikeSpot)
    # Assign the motorbike to the spot
    available_spot.assign_vehicle(motorbike)
    # Mark the spot as occupied
    available_spot.is_free = False
  