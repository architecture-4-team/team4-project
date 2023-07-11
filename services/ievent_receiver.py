from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from model.user import UserExt
from utils.call_state import CallState


class EventType(str, Enum):
    # connection
    CLIENT_CONNECTED = 'client-connected'
    CLIENT_DISCONNECTED = 'client-disconnected'

    # data
    TCP_DATA_RECEIVED = 'tcp-data'
    UDP_DATA_RECEIVED = 'udp-data'

    # user login / logout / lost connection
    USER_ADDED = 'user-added'
    USER_REMOVED = 'user-removed'

    # room state
    STATE_CHANGED = 'state-changed'
    USER_JOINED = 'user-joined'
    USER_LEAVED = 'user=leaved'


@dataclass
class EventPayload:
    pass


@dataclass
class TCPPayload(EventPayload):
    socket: Any


@dataclass
class UDPPayload(EventPayload):
    sender_ip: str
    receive_port: str
    packet: Any


@dataclass
class UserPayload(EventPayload):
    user: UserExt


@dataclass
class RoomPayload(EventPayload):
    room: Any   # CallRoom (circular reference)
    state: CallState


class IEventReceiver(metaclass=ABCMeta):
    @abstractmethod
    def receive(self, event_name: EventType, payload):
        pass
