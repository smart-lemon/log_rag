from code.library_administration.definitions import *


class Account(ABC):
    def __init__(self, id, password, person, status=AccountStatus.ACTIVE):
        self.id = id
        self.password = password
        self.status = status
        self.person = person

    def reset_password(self, new_password="" ):
        self.__password = new_password
        log_message(self.__class__.__name__, __name__, "SPassword has been successfully reset.")
