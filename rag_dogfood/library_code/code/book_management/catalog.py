from code.book_management.search import Search
import sqlite3
from code.utilities.utils import *

class Catalog(Search):
    def __init__(self):
        log_message(self.__class__.__name__, __name__, "Initializing Catalog instance")
        self.__book_titles = {}
        self.__book_authors = {}
        self.__book_subjects = {}
        self.__book_publication_dates = {}

        def search_by_title(self, query):
            log_message(self.__class__.__name__, __name__, "Searching by title")
            conn = sqlite3.connect("../../library.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{query}%",))
            books = cursor.fetchall()
            conn.close()

            log_message(self.__class__.__name__, __name__, "Returning books matching the title query")
            return [
                {
                    "ISBN": book[0],
                    "title": book[1],
                    "subject": book[2],
                    "publisher": book[3],
                    "language": book[4],
                    "number_of_pages": book[5]
                }
                for book in books
            ]


def search_by_author(self, query):
    log_message(self.__class__.__name__, __name__, "Searching by author")
    conn = sqlite3.connect("../../library.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT books.ISBN, books.title, books.subject, books.publisher, books.language, books.number_of_pages
        FROM books
        JOIN book_authors ON books.ISBN = book_authors.ISBN
        WHERE book_authors.author_name LIKE ?
        """, (f"%{query}%",))
    books = cursor.fetchall()
    conn.close()

    log_message(self.__class__.__name__, __name__, "Returning books matching the author query")
    return [
        {
            "ISBN": book[0],
            "title": book[1],
            "subject": book[2],
            "publisher": book[3],
            "language": book[4],
            "number_of_pages": book[5]
        }
        for book in books
    ]
