from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot


class Login(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str, object)
    def receive_message(self, message, client_socket):
        print(f'receive : {message}, {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}')