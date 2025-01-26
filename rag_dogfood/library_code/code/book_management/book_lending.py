from code.library_administration.definitions import *

import sqlite3
from code.utilities.utils import *

class BookLending:
    def __init__(self, creation_date, due_date, book_item_barcode, member_id):
        log_message(self.__class__.__name__, __name__, "Initializing BookLending instance")
        self.creation_date = creation_date
        self.due_date = due_date
        self.return_date = None
        self.book_item_barcode = book_item_barcode
        self.member_id = member_id

    @staticmethod
    def lend_book(barcode, member_id):
        log_message("BookLending", __name__, "Lending a book")
        conn = sqlite3.connect("./library.db")
        cursor = conn.cursor()

        log_message("BookLending", __name__, "Checking if the book is already lent out")
        cursor.execute("SELECT * FROM book_lending WHERE barcode = ? AND return_date IS NULL", (barcode,))
        if cursor.fetchone():
            log_message("BookLending", __name__, "Book is already lent out")
            conn.close()
            return False

        log_message("BookLending", __name__, "Adding a new lending record")
        due_date = (datetime.now() + timedelta(days=LibConstants.MAX_LENDING_DAYS)).strftime("%Y-%m-%d")
        cursor.execute("""
         INSERT INTO book_lending (barcode, member_id, creation_date, due_date, return_date)
         VALUES (?, ?, ?, ?, NULL)
         """, (barcode, member_id, datetime.now().strftime("%Y-%m-%d"), due_date))

        conn.commit()
        conn.close()
        log_message("BookLending", __name__, "Book lent successfully")
        return True

    @staticmethod
    def fetch_lending_details(barcode):
        log_message("BookLending", __name__, "Fetching lending details")
        conn = sqlite3.connect("./library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book_lending WHERE barcode = ? AND return_date IS NULL", (barcode,))
        lending_details = cursor.fetchone()
        conn.close()

        log_message("BookLending", __name__, "Returning fetched lending details")
        if lending_details:
            return {
                "barcode": lending_details[0],
                "member_id": lending_details[1],
                "creation_date": lending_details[2],
                "due_date": lending_details[3],
                "return_date": lending_details[4]
            }
        return None

