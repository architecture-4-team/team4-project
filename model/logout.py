from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from model.user import User
from model.directory_singleton import directory_service


class LogOut(QObject):
    def __init__(self):
        super().__init__()

    @staticmethod
    def do_process(uuid):
        # db 에 해당 값이 있는지 확인한다
        ret, user = directory_service.search_by_uuid(uuid)
        if ret:
            directory_service.remove(user)

        directory_service.print_info()
        return True, user
