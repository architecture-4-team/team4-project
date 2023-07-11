import uuid
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot
from model.user import UserExt
from model.directory_singleton import directory_service
from services.storage_manager import storage_manager
from utils.call_state import CallState


class Login(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str, object)
    def receive_message(self, message, client_socket):
        print(f'receive : {message}, {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}')

    @staticmethod
    def do_process(email, uuid, socket):
        # db 에 해당 값이 있는지 확인한다
        user = storage_manager.get_user_by_email(email)
        userext = UserExt(uuid=user.uuid, contact_id=user.contact_id, email=user.email, pwd=user.pwd,
                          firstname=user.firstname, lastname=user.lastname, ip=user.ip, online=user.online,
                          enable=user.enable, summary=user.summary, question1=user.question1,
                          question2=user.question2, question3=user.question3,
                          created_at=user.created_at, updated_at=user.updated_at)
        # 값이 있으면 uuid 를 할당해서 리턴한다 (값이 없으면 False, None 을 리턴한다 )
        # user_uuid = uuid.uuid4()

        # User 객체 생성 후 directory service 에 넣는다.
        # user = UserExt(socket_info=socket)
        userext.socket_info = socket
        userext.set_state(CallState.IDLE)

        directory_service.append(userext)
        directory_service.print_info()

        return True, userext.uuid
