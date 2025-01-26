from enum import Enum
from abc import ABC, abstractmethod

class ReservationStatus(Enum):
    WAITING, PENDING, CANCELED, NONE, COMPLETED = 1, 2, 3, 4, 5


class AccountStatus(Enum):
    ACTIVE, CLOSED, CANCELED, BLACKLISTED, NONE = 1, 2, 3, 4, 5


class Address:
    def __init__(self, street, city, state, zip_code, country):
        self.street_address = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country


class Person(ABC):
    def __init__(self, name, address, email, phone):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone


class LibConstants:
    MAX_BOOKS_ISSUED_TO_A_USER = 5
    MAX_LENDING_DAYS = 10

    def __init__(self):
        self.MAX_BOOKS_ISSUED_TO_A_USER = 5
        self.MAX_LENDING_DAYS = 10
