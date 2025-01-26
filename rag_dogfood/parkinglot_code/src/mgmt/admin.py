from src.utilities.utils import *
from src.utilities.definitions import *

# Admin Class
class Admin:
    def __init__(self, user_name, password, db):
        self.user_name = user_name
        self.password = password
        self.db = db
        self.add_to_db()

    def add_to_db(self):
        try:
            self.db.cursor.execute("INSERT INTO accounts (user_name, password, status) VALUES (?, ?, ?)",
                                   (self.user_name, self.password, AccountStatus.ACTIVE.value))
            self.db.conn.commit()
            log_message(self.__class__.__name__, __name__, f"Admin {self.user_name} added to database.")
        except Exception as e:
            log_message(self.__class__.__name__, __name__, f"Error adding admin {self.user_name}: {e}")

    def add_parking_spot(self, spot_number, spot_type):
        try:
            self.db.cursor.execute("INSERT INTO parking_spots (spot_number, type, is_free) VALUES (?, ?, ?)",
                                   (spot_number, spot_type.value, 1))
            self.db.conn.commit()
            log_message(self.__class__.__name__, __name__, f"Parking spot {spot_number} added.")
        except Exception as e:
            log_message(self.__class__.__name__, __name__, f"Error adding parking spot {spot_number}: {e}")