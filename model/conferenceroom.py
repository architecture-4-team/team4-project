import json
from typing import List

from model.conferencecall_broker import conferencecallbroker
from utils.call_state import CallState
from model.user import UserExt
from services.network_manager import NetworkManager
from model.directory_singleton import directory_service


class ConferenceRoom:
    participants: List[UserExt] = list()

    def __init__(self, number):
        self.room_id = '0'
        self.number_of_participants = number
        participants = [user for user in directory_service.users[:number] if user.get_state() == CallState.IDLE]
        #self.room_members: UserExt = [] # 복합시나리오에서 사용 (데모용으로는 단순시나리오만 대응)
        self.call_state = CallState.IDLE

    def set_room_id(self, roomid):
        self.room_id = roomid

    def set_state(self, state):
        pre_state = self.call_state
        self.call_state = state
        if pre_state != self.call_state:
            self.proceed_next_step(state)

    def set_user_callstate(self, uuid, call_state):
        for user in self.participants:
            if user.uuid == uuid:
                user.set_state(call_state)
                conferencecallbroker.state_changed(room_id=self.room_id, state=call_state, user=user)
                return user

    def get_participants_number(self):
        return len(self.participants)

    def get_participated_members(self):
        count = 0
        for user in self.participants:
            if user.get_state() == CallState.CONFERENCE_CALLING:
                count = count + 1
        return count

    def print_users_call_states(self):
        for user in self.participants:
            print(f'\t\t{user.email} : {user.get_state()}')

    def proceed_next_step(self, state):
        if state == CallState.LEAVE:
            self.call_state = CallState.IDLE
            pass

        elif state == CallState.JOIN:
            for user in self.participants:
                data = '''{
                    "command": "JOIN",
                    "contents": {
                        "uuid": "%s",
                        "roomid": "%s",
                        "participants":"%s"
                      }
                    }''' % (user.uuid, self.room_id,
                            [u.email for u in self.participants if u is not user])
                data_json = json.loads(data)
                ret_data_json = json.dumps(data_json)
                NetworkManager.send_tcp_data(ret_data_json.encode(),
                                             user.socket_info)
                user.set_state(CallState.JOIN)
            pass
        elif state == CallState.CONFERENCE_CALLING:
            pass

        conferencecallbroker.state_changed(self.room_id, state)
