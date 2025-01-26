import sqlite3
import logging
import os
import definitions
from utils import *

# Database setup
# Database setup
class ParkingLotDB:
    def __init__(self, db_name="../parking_lot.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        log_message(self.__class__.__name__, __name__, "Database initialized.")

    def create_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE,
                password TEXT,
                status INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_number TEXT UNIQUE,
                type INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS parking_spaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spot_number TEXT UNIQUE,
                type INTEGER,
                is_free BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS parking_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                spot_id INTEGER,
                status INTEGER,
                issue_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY(spot_id) REFERENCES parking_spaces(id)
            );
            
            CREATE TABLE IF NOT EXISTS parking_floors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                floor_number INTEGER UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS entrance_panels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                panel_id TEXT UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS exit_panels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                panel_id TEXT UNIQUE
            );
        ''')
        self.conn.commit()
        log_message(self.__class__.__name__, __name__, "Database tables created or verified.")

    def close(self):
        self.conn.close()
        log_message(self.__class__.__name__, __name__, "Database connection closed.")

