from enum import Enum


class CallState(Enum):
    IDLE = 0
    INVITE = 1
    CALLING = 2
    ACCEPT = 3
    BYE = 4
    CANCEL = 5
    # conference 에 대한 확장 필요
    MAX = 4
