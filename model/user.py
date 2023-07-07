from dataclasses import dataclass
from datetime import datetime
from utils.call_state import CallState


@dataclass
class User:
    uuid: str
    contact_id: str
    email: str
    password: str
    firstname: str
    lastname: str
    ip: str
    status: str
    summary: str
    created_at: datetime
    updated_at: datetime


@dataclass()
class UserExt(User):
    # call_state: CallState.IDLE
    # socket_info: None

    def set_state(self, call_state):
        self.call_state = call_state

    def set_socket(self, socket):
        self.socket_info = socket

    def get_state(self):
        return self.call_state
