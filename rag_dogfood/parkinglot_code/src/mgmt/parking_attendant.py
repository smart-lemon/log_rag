from src.mgmt.account import *

class ParkingAttendant(Account):
    def __init__(self, user_name, password, person, status=AccountStatus.ACTIVE):
        super().__init__(user_name, password, person, status)

    def process_ticket(self, ticket_number):
        log_message(self.__class__.__name__, __name__, f"The attendent looks at the ticket suspiciously {ticket_number} ")