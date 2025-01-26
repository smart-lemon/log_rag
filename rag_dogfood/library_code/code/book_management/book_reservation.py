import sqlite3
from code.utilities.utils import *

class BookReservation:
    def __init__(self, creation_date, status, book_item_barcode, member_id):
        log_message(self.__class__.__name__, __name__, "Initializing BookReservation instance")
        self.creation_date = creation_date
        self.status = status
        self.book_item_barcode = book_item_barcode
        self.member_id = member_id

    @staticmethod
    def fetch_reservation_details(barcode):
        log_message("BookReservation", "fetch_reservation_details", "Fetching reservation details.")
        conn = sqlite3.connect("./library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book_reservations WHERE book_item_barcode = ?", (barcode,))
        reservation_details = cursor.fetchone()
        conn.close()
        if reservation_details:
            log_message("BookReservation", "fetch_reservation_details",
                        f"Reservation details found: {reservation_details}.")
        else:
            log_message("BookReservation", "fetch_reservation_details", "No reservation details found.")
            return None


        return BookReservation(
            creation_date=reservation_details[1],  # Assuming 'creation_date' is at index 1
            status=reservation_details[2],  # Assuming 'status' is at index 2
            book_item_barcode=reservation_details[3],  # Assuming 'book_item_barcode' is at index 3
            member_id=reservation_details[4]  # Assuming 'member_id' is at index 4
        )
