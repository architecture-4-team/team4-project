from enum import Enum


class CallState(Enum):
    IDLE = 0
    INVITE = 1
    CALLING = 2
    ACCEPT = 3
    BYE = 4
    CANCEL = 5
    # conference 에 대한 확장
    JOIN = 6
    CONFERENCE_CALLING = 7
    LEAVE = 8

    MAX = 9
