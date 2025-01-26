from src.utilities.definitions import *

from datetime import datetime
from enum import Enum
from abc import ABC

class VehicleType(Enum):
    CAR = 1
    TRUCK = 2
    ELECTRIC = 3
    VAN = 4
    MOTORBIKE = 5

class ParkingSpotType(Enum):
    HANDICAPPED = 1
    COMPACT = 2
    LARGE = 3
    MOTORBIKE = 4
    ELECTRIC = 5

class AccountStatus(Enum):
    ACTIVE = 1
    BLOCKED = 2
    BANNED = 3
    COMPROMISED = 4
    ARCHIVED = 5
    UNKNOWN = 6

class ParkingTicketStatus(Enum):
    ACTIVE = 1
    PAID = 2
    LOST = 3