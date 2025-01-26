import random
import os

# Database setup
def clean_db():
    db_path = "../library.db"
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    clean_db()
