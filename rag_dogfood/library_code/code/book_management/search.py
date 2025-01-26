from abc import ABC, abstractmethod
import sqlite3
from code.utilities.utils import *

class Search(ABC):
    def search_by_title(self, title):
        None

    def search_by_author(self, author):
        None

    def search_by_subject(self, subject):
        None

    def search_by_pub_date(self, publish_date):
        None

