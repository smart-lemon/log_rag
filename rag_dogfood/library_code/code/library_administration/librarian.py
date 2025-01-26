from code.library_administration.definitions import *
from code.library_administration.account import *
from code.utilities.utils import *
import sqlite3

class Librarian(Account):
    def __init__(self, id, password, person, status=AccountStatus.ACTIVE):
        super().__init__(id, password, person, status)

    def add_book_item(self, book_item):
        conn = sqlite3.connect("./library.db")
        cursor = conn.cursor()
        cursor.execute("""
    INSERT INTO books (barcode, title, subject, publisher, language, number_of_pages, price, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (book_item.barcode, book_item.title, book_item.subject, book_item.publisher,
          book_item.language, book_item.number_of_pages, book_item.price, book_item.status.name))
        conn.commit()
        conn.close()
        print()
        log_message(self.__class__.__name__, __name__, "Book item added successfully.")

    def block_member(self, member):
        member.status = AccountStatus.Blocked
        print()
        log_message(self.__class__.__name__, __name__, f"Member {member.__id} has been blocked.")


    def un_block_member(self, member):
        member.status = AccountStatus.Active
        log_message(self.__class__.__name__, __name__, f"Member {member.__id} has been unblocked.")
