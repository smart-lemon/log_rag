from src.utilities.utils import *
from src.utilities.definitions import *


class Account:
    def __init__(self, user_name, password, person, status=AccountStatus.ACTIVE):
        self.__user_name = user_name
        self.__password = password
        self.__person = person
        self.__status = status

    def reset_password(self):
        log_message(self.__class__.__name__, __name__, f"Reset of password {self.__user_name} completed")
