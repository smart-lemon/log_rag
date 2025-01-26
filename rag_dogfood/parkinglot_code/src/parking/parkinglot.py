from src.utilities.utils import *
from src.utilities.definitions import *
from src.parking.parkingrate import *
from src.parking.parkingticket import *
from src.parking.parkingspot import *
import threading

class ParkingLot:
    # Singleton ParkingLot to ensure only one object of ParkingLot in the system,
    # all entrance panels will use this object to create new parking ticket: get_new_parking_ticket(),
    # similarly exit panels will also use this object to close parking tickets
    instance = None

    class __OnlyOne:
        def __init__(self, name, address):
            # 1. initialize variables: read name, address and parking_rate from database
            # 2. initialize parking floors: read the parking floor map from database,
            #    this map should tell how many parking spots are there on each floor. This
            #    should also initialize max spot counts too.
            # 3. initialize parking spot counts by reading all active tickets from database
            # 4. initialize entrance and exit panels: read from database
            self.__name = name
            self.__address = address
            self.__parking_rate = ParkingRate()

            self.__compact_spot_count = 0
            self.__large_spot_count = 0
            self.__motorbike_spot_count = 0
            self.__electric_spot_count = 0
            self.__max_compact_count = 0
            self.__max_large_count = 0
            self.__max_motorbike_count = 0
            self.__max_electric_count = 0

            self.__entrance_panels = {}
            self.__exit_panels = {}
            self.__parking_floors = {}

            # all active parking tickets, identified by their ticket_number
            self.__active_tickets = {}

            self.__lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(ParkingLot, cls).__new__(cls)
            cls.instance.__only_one_instance = ParkingLot.__OnlyOne(*args, **kwargs)
        return cls.instance

    def __init__(self, name, address):
        # Ensure that __init__ is only called once
        if not hasattr(self, '_ParkingLot__initialized'):
            self.__only_one_instance = self.instance.__only_one_instance
            self.__initialized = True

    def __getattr__(self, name):
        return getattr(self.__only_one_instance, name)

    def find_available_spot(self, vehicle):
        self.increment_spot_count(vehicle)
        log_message(self.__class__.__name__, __name__, f"Finding spot {vehicle} ")
        return ParkingSpot(vehicle,  self._OnlyOne__max_compact_count)

    def free_spot(self, vehicle):
        self.decrement_spot_count(vehicle.get_type())
        log_message(self.__class__.__name__, __name__, f"Freeing spot {vehicle} ")
        return ParkingSpot(vehicle,  self._OnlyOne__electric_spot_count).remove_vehicle()

    def get_new_parking_ticket(self, vehicle):
        log_message(self.__class__.__name__, __name__, f"Creating new parking spot {vehicle} ")
        try:
            if self.is_full(vehicle.get_type()):
                raise Exception('Parking full!')
        except:
            log_message(self.__class__.__name__, __name__, f"Parking full {vehicle} ")
            # Synchronizing to allow multiple entrances panels to issue a new
        # parking ticket without interfering with each other    self.__lock.acquire()
        ticket = ParkingTicket()
        vehicle.assign_ticket(ticket)
        # ticket.save_in_DB()

        # If the ticket is successfully saved in the database, we can increment the parking spot count
        self.increment_spot_count(vehicle.get_type())
        self._OnlyOne__active_tickets[ticket.get_parking_ticket()] = ticket
        # self._OnlyOne__active_tickets.put(ticket.get_ticket_number(), ticket)
       #  self.__lock.release()
        return ticket

    def close_parking_ticket(self, ticket):

        log_message(self.__class__.__name__, __name__, f"Closing parking ticket {ticket} ")

    def is_full(self, type):
        # trucks and vans can only be parked in LargeSpot
        if type == VehicleType.TRUCK or type == VehicleType.VAN:
            return self.__large_spot_count >= self.__max_large_count

        # motorbikes can only be parked at motorbike spots
        if type == VehicleType.MOTORBIKE:
            return self.__motorbike_spot_count >= self.__max_motorbike_count

        # cars can be parked at compact or large spots
        if type == VehicleType.CAR:
            return (self._OnlyOne__compact_spot_count + self._OnlyOne__large_spot_count) >= (
                    self._OnlyOne__max_compact_count + self._OnlyOne__max_large_count)

        # electric car can be parked at compact, large or electric spots
        return (self._OnlyOne__compact_spot_count + self._OnlyOne__large_spot_count + self._OnlyOne__electric_spot_count) >= (
                self._OnlyOne__max_compact_count + self._OnlyOne__max_large_count
                + self._OnlyOne__max_electric_count)

    def increment_spot_count(self, type):
        if type == VehicleType.TRUCK or type == VehicleType.VAN:
            self._OnlyOne__large_spot_count += 1
        elif type == VehicleType.MOTORBIKE:
            self._OnlyOne__motorbike_spot_count += 1
        elif type == VehicleType.CAR:
            if self._OnlyOne__compact_spot_count < self._OnlyOne__max_compact_count:
                self._OnlyOne__compact_spot_count += 1
            else:
                self._OnlyOne__large_spot_count += 1
        else:  # electric car
            if self._OnlyOne__electric_spot_count < self._OnlyOne__max_electric_count:
                self._OnlyOne__electric_spot_count += 1
            elif self._OnlyOne__compact_spot_count < self._OnlyOne__max_compact_count:
                self._OnlyOne__compact_spot_count += 1
            else:
                self._OnlyOne__large_spot_count += 1

    def decrement_spot_count(self, type):
        if type == VehicleType.TRUCK or type == VehicleType.VAN:
            self._OnlyOne__large_spot_count -= 1
        elif type == VehicleType.MOTORBIKE:
            self._OnlyOne__motorbike_spot_count -= 1
        elif type == VehicleType.CAR:
            if self._OnlyOne__compact_spot_count < self._OnlyOne__max_compact_count:
                self._OnlyOne__compact_spot_count -= 1
            else:
                self._OnlyOne__large_spot_count -= 1
        else:  # electric car
            if self._OnlyOne__electric_spot_count < self._OnlyOne__max_electric_count:
                self._OnlyOne__electric_spot_count -= 1
            elif self._OnlyOne__compact_spot_count < self._OnlyOne__max_compact_count:
                self._OnlyOne__compact_spot_count -= 1
            else:
                self._OnlyOne__large_spot_count -= 1

    def add_parking_floor(self, floor_number):
        log_message(self.__class__.__name__, __name__, f"Creating a new floor {floor_number} ")
        try:
            self.db.cursor.execute("INSERT INTO parking_floors (floor_number) VALUES (?)", (floor_number,))
            self.db.conn.commit()
            log_message(self.__class__.__name__, __name__, f"Parking floor {floor_number} added.")
        except Exception as e:
            log_message(self.__class__.__name__, __name__, f"Error adding parking floor {floor_number}: {e}")

    def add_entrance_panel(self, panel_id):
        log_message(self.__class__.__name__, __name__, f"Associating a new panel {panel_id} ")
        try:
            self.db.cursor.execute("INSERT INTO entrance_panels (panel_id) VALUES (?)", (panel_id,))
            self.db.conn.commit()
            log_message(self.__class__.__name__, __name__, f"Entrance panel {panel_id} added.")
        except Exception as e:
            log_message(self.__class__.__name__, __name__, f"Error adding entrance panel {panel_id}: {e}")

    def add_exit_panel(self, panel_id):
        log_message(self.__class__.__name__, __name__, f"Associating a new exit panel {panel_id}")
        try:
            self.db.cursor.execute("INSERT INTO exit_panels (panel_id) VALUES (?)", (panel_id,))
            self.db.conn.commit()
            log_message(self.__class__.__name__, __name__, f"Exit panel {panel_id} added.")
        except Exception as e:
            log_message(self.__class__.__name__, __name__, f"Error adding exit panel {panel_id}: {e}")
