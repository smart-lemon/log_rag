# Import necessary modules
from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.vehicle.vehicle_types import *

if __name__ == "__main__":
    # Import necessary modules

    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Create an electric car object
    electric_car = ElectricCar("PQR012")
    # Get a parking ticket
    ticket = parking_lot.get_new_parking_ticket(electric_car)
    # Find an available electric spot
    available_spot = parking_lot.find_available_spot(ElectricSpot)
    # Assign the electric car to the spot
    available_spot.assign_vehicle(electric_car)
    # Mark the spot as occupied
    available_spot.is_free = False