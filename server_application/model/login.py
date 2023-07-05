import uuid
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot


class Login(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str, object)
    def receive_message(self, message, client_socket):
        print(f'receive : {message}, {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}')

    @staticmethod
    def do_process(email, password):
        # db 에 해당 값이 있는지 확인한다
        # 값이 있으면 uuid 를 할당해서 리턴한다 (값이 없으면 False, None 을 리턴한다 )
        user_uuid = uuid.uuid4()
        return True, user_uuid
