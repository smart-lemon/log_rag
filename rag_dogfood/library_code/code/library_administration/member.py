# For simplicity, we are not defining getter and setter functions. The reader can
# assume that all class attributes are private and accessed through their respective
# public getter methods and modified only through their public methods function.
import datetime
from datetime import date
from code.book_management.book_reservation import *
from code.book_management.book_lending import *
from code.library_administration.fine import *
from code.library_administration.account import *
from code.library_administration.definitions import *
from code.book_management.definitions import *


class Member(Account):
    def __init__(self, id, password, person, status=AccountStatus.ACTIVE):
        super().__init__(id, password, person, status)
        self.date_of_membership = date.today()
        self.total_books_checkedout = 0
        log_message("Member", "__init__", "Member object created.")

    def get_total_books_checked_out(self):
        log_message("Member", "get_total_books_checkedout", "Fetching total books checked out.")
        return self.total_books_checkedout

    def reserve_book_item(self, book_item):
        conn = sqlite3.connect("../library.db")
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO book_reservations (creation_date, status, book_item_barcode, member_id)
        VALUES (?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d"), ReservationStatus.WAITING.name, book_item.barcode, self.id))
        conn.commit()
        conn.close()
        log_message("Member", "reserve_book_item", "Book item reserved successfully.")

    def increment_total_books_checkedout(self):
        self.total_books_checkedout += 1
        log_message("Member", "increment_total_books_checkedout", "Incremented total books checked out.")

    def renew_book_item(self, book_item):
        self.check_for_fine(book_item.get_barcode())
        book_reservation = BookReservation.fetch_reservation_details(book_item.get_barcode())
        # check if this book item has a pending reservation from another member
        if book_reservation != None and book_reservation.get("member_id") != self.id:

            self.__total_books_checkedout -= 1
            book_item.update_book_item_status(BookStatus.RESERVED)
            return False
        elif book_reservation != None:
            # book item has a pending reservation from this member
            book_reservation["status"] = ReservationStatus.COMPLETED
        BookLending.lend_book(book_item.barcode, self.id)
        book_item.update_due_date(
            datetime.now() + timedelta(days=LibConstants.MAX_LENDING_DAYS))
        log_message("Member", "renew_book_item", "Book item renewed successfully.")
        return True

    def checkout_book_item(self, book_item):
        if self.get_total_books_checked_out() >= LibConstants.MAX_BOOKS_ISSUED_TO_A_USER:
            log_message("Member", "checkout_book_item", "User has already checked out the maximum number of books.")
            return False
        book_reservation = BookReservation.fetch_reservation_details(book_item.barcode)
        if book_reservation != None and book_reservation.member_id != self.id:
            log_message("Member", "checkout_book_item", "Book is reserved by another member.")
            return False
        elif book_reservation != None:
            # book item has a pending reservation from the give member, update it
            book_reservation.status = ReservationStatus.COMPLETED

        if not book_item.checkout(self.id):
            log_message("Member", "checkout_book_item", "Failed to checkout book item.")
            return False

        self.increment_total_books_checkedout()
        log_message("Member", "checkout_book_item", "Book item checked out successfully.")
        return True

    def check_for_fine(self, book_item_barcode):
        book_lending = BookLending.fetch_lending_details(book_item_barcode)
        due_date = book_lending['due_date']
        log_message("Member", "renew_book_item", "Due date is " + due_date)
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

        today = date.today()

        # check if the book has been returned within the due date
        if today > due_date:
            diff = today - due_date
            diff_days = diff.days
            Fine.collect_fine(self.get_member_id(), diff_days)
            log_message("Member", "check_for_fine", f"Fine collected for {diff_days} days.")

    def return_book_item(self, book_item):
        self.check_for_fine(book_item.barcode)
        book_reservation = BookReservation.fetch_reservation_details(
            book_item.barcode)
        if book_reservation != None:
            # book item has a pending reservation
            book_item.status = BookStatus.RESERVED
            # book_reservation.send_book_available_notification()
            log_message("Member", "return_book_item", "Book item marked as reserved and notification sent.")
        book_item.status = BookStatus.AVAILABLE
        log_message("Member", "return_book_item", "Book item returned successfully.")

    def renew_book_item(self, book_item):
        self.check_for_fine(book_item.barcode)
        book_reservation = BookReservation.fetch_reservation_details(
            book_item.barcode)
        # check if self book item has a pending reservation from another member
        if book_reservation != None and book_reservation.member_id != self.id:
            log_message("Member", "renew_book_item", "Book is reserved by another member.")
            self.decrement_total_books_checkedout()
            book_item.update_book_item_state(BookStatus.RESERVED)
            book_reservation.send_book_available_notification()
            return False
        elif book_reservation != None:
            # book item has a pending reservation from self member
            book_reservation.status = ReservationStatus.COMPLETED
        BookLending.lend_book(book_item.barcode, self.id)
        book_item.due_date = datetime.now() + timedelta(days=LibConstants.MAX_LENDING_DAYS)
        log_message("Member", "renew_book_item", "Book item renewed successfully.")
        return True
