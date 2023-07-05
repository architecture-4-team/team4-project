import uuid
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from model.user import User
from model.directory_singleton import directory_service


class Login(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str, object)
    def receive_message(self, message, client_socket):
        print(f'receive : {message}, {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}')

    @staticmethod
    def do_process(email, password, socket):
        # db 에 해당 값이 있는지 확인한다
        # 값이 있으면 uuid 를 할당해서 리턴한다 (값이 없으면 False, None 을 리턴한다 )
        user_uuid = uuid.uuid4()

        # User 객체 생성 후 directory service 에 넣는다.
        user = User(email_id=email,
                    contact_id=email+'_contact',
                    uuid=user_uuid,
                    firstname='CHOO',
                    lastname='JM',
                    socket_info=socket)

        directory_service.append(user)
        directory_service.print_info()

        return True, user_uuid
