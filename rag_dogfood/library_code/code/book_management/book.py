from code.book_management.book_lending import *
from code.book_management.definitions import *


class Book(ABC):
    def __init__(self, ISBN, title, subject, publisher, language, number_of_pages):
        self.ISBN = ISBN
        self.title = title
        self.subject = subject
        self.publisher = publisher
        self.language = language
        self.number_of_pages = number_of_pages
        self.authors = []


class BookItem(Book):
    def __init__(self, ISBN, title, subject, publisher, language, number_of_pages, barcode,
                 is_reference_only, borrowed, due_date, price, book_format, status,
                 date_of_purchase, publication_date, placed_at):
        # Call the parent constructor (Book) to initialize its attributes
        super().__init__(ISBN, title, subject, publisher, language, number_of_pages)

        self.barcode = barcode
        self.is_reference_only = is_reference_only
        self.borrowed = borrowed
        self.due_date = due_date
        self.price = price
        self.format = book_format
        self.status = status
        self.date_of_purchase = date_of_purchase
        self.publication_date = publication_date
        self.placed_at = placed_at

    def checkout(self, member_id):
        if self.is_reference_only:
            print("self book is Reference only and can't be issued")
            return False
        if not BookLending.lend_book(self.barcode, member_id):
            return False
        self.status = BookStatus.LOANED
        return True



