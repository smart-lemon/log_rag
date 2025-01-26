# Import necessary modules
from src.parking.parkinglot import ParkingLot
from src.parking.electricspot import *
from src.parking.compactspot import *
from src.vehicle.vehicle_types import *
from src.mgmt.parking_attendant import *

if __name__ == "__main__":
    # Import necessary modules

    # Initialize the parking lot
    parking_lot = ParkingLot("My Parking Lot", "123 Main St")
    # Get the car's ticket number
    ticket_number = "ABC123"
    # Validate the ticket
    attendent = ParkingAttendant("Thomas", "None", AccountStatus.ACTIVE)
    valid_ticket = attendent.process_ticket(ticket_number)
    electric_car = ElectricCar("STU345")
    # If the ticket is valid, open the barrier and
    # Mark the spot as free
    parking_lot.free_spot(electric_car)