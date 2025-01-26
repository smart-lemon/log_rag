import random
import string
from code.utilities.utils import *
from code.book_management.catalog import *
from code.book_management.book import *
from code.library_administration.account import  *
from code.library_administration.librarian import  *
from code.library_administration.member import  *
from code.library_administration.definitions import *
from code.library_administration.rack import *
from code.book_management.definitions import *


# Database setup
def initialize_db():
    db_path = "../library.db"
    if os.path.exists(db_path):
        log_message("Database", "initialize_database", "Database already exists. Skipping initialization.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        barcode TEXT PRIMARY KEY,
        isbn TEXT,
        title TEXT,
        subject TEXT,
        publisher TEXT,
        language TEXT,
        pages INTEGER,
        is_reference_only INTEGER,
        status INTEGER,
        due_date TEXT, 
        number_of_pages INTEGER,
        price INTEGER
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date TEXT NOT NULL,
            status INTEGER NOT NULL,
            book_item_barcode TEXT NOT NULL,
            member_id TEXT NOT NULL,
            FOREIGN KEY (book_item_barcode) REFERENCES books (barcode),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
        """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        status INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_lending (
        barcode TEXT,
        member_id TEXT,
        creation_date TEXT,
        due_date TEXT,
        return_date TEXT,
        FOREIGN KEY (barcode) REFERENCES books (barcode),
        FOREIGN KEY (member_id) REFERENCES members (id)
    )
    """)

    conn.commit()
    conn.close()


# Testing basic use cases
def test_library_system():
    initialize_db()

    # Creating a librarian and member
    librarian = Librarian("librarian1", "password123", Person("John Doe", "123 Main St", "johndoe@example.com", "555-5555"))
    member = Member("member1", "password456", Person("Jane Smith", "456 Elm St", "janesmith@example.com", "555-1234"))

    book_item1 = BookItem(
        ISBN="1234567890",
        title="Python Programming",
        subject="Education",
        publisher="Tech Press",
        language="English",
        number_of_pages=500,
        barcode="barcode".join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        is_reference_only=False,
        price=50.0,
        book_format="Hardcover",
        status=BookStatus.AVAILABLE,
        date_of_purchase=datetime.now(),
        borrowed=datetime.now() + timedelta(days=-5, hours=-5),
        due_date=datetime.now() + timedelta(days=5, hours=-5),
        publication_date=datetime.now() - timedelta(days=365),
        placed_at=Rack(1, "A1")
    )

    book_item2 = BookItem(
        ISBN="0987765564",
        title="C++ Programming",
        subject="Education",
        publisher="Tech Press",
        language="English",
        number_of_pages=500,
        barcode="barcode".join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        is_reference_only=False,
        price=50.0,
        book_format="Hardcover",
        status=BookStatus.AVAILABLE,
        date_of_purchase=datetime.now(),
        publication_date=datetime.now() - timedelta(days=365),
        borrowed=datetime.now() + timedelta(days=-5, hours=-5),
        due_date=datetime.now() + timedelta(days=5, hours=-5),
        placed_at=Rack(1, "A1")
    )

    # 1. Add book items to the library
    librarian.add_book_item(book_item1)
    librarian.add_book_item(book_item2)

    # Negative scenarios
    # 1. Member tries to check out a reference-only book
    book_item1.is_reference_only = True
    member.checkout_book_item(book_item1)

    # 2. Member tries to reserve a checked-out book
    book_item1.is_reference_only = False
    member.checkout_book_item(book_item1)
    member.reserve_book_item(book_item1)

    # 3. Member tries to check out a reserved book by another member
    other_member = Member("member2", "password789", Person("Alice Brown", "789 Pine St", "alice@example.com", "555-6789"))
    other_member.reserve_book_item(book_item2)
    member.checkout_book_item(book_item2)

    # 4. Member exceeds the book limit
    for _ in range(LibConstants.MAX_BOOKS_ISSUED_TO_A_USER):
        member.increment_total_books_checkedout()
    member.checkout_book_item(book_item1)

    # 5. Renewing a book reserved by another member
    other_member.reserve_book_item(book_item1)

    # 6. Returning a book and failing to mark it available
    book_item1.update_book_item_status = lambda x: None  # Mock failure
    member.return_book_item(book_item1)

    # 7. Trying to fetch lending details for a non-existent book
    BookLending.fetch_lending_details("invalid_barcode")

    # 8. Trying to collect fine for a book with no overdue
    Fine(datetime.now(), "0987765564", "member1").collect_fine("member1", 00)

    # 9. Trying to add a duplicate book item
    try:
        librarian.add_book_item(book_item1)
    except Exception as e:
        assert "UNIQUE constraint" in str(e)

    # 10. Searching for a non-existent book
    catalog = Catalog()
    results = catalog.search_by_title("Nonexistent Book")

if __name__ == "__main__":
    test_library_system()
