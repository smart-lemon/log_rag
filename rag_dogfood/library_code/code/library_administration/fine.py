from code.utilities.utils import *

class Fine:
    def __init__(self, creation_date, book_item_barcode, member_id):
        log_message(self.__class__.__name__, __name__, "Initializing Fine instance")
        self.creation_date = creation_date
        self.book_item_barcode = book_item_barcode
        self.member_id = member_id

    def collect_fine(self, member_id, days):
        log_message(self.__class__.__name__, __name__, "Collecting fine")
        fine_per_day = 5  # Assuming a fine of $5 per day
        total_fine = fine_per_day * days
        log_message(self.__class__.__name__, __name__, f"Fine collected: ${total_fine} for {days} overdue days")
        return total_fine

