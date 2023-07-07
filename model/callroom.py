import json
from utils.call_state import CallState
from model.user import User, UserExt
from services.network_manager import NetworkManager


class CallRoom:
    def __init__(self, sender, receiver, network_manager):
        self.call_id = '0'
        self.sender_user: UserExt = sender
        self.receiver_user: UserExt = receiver
        self.network_manager: NetworkManager = network_manager
        self.call_state = CallState.IDLE  # IDLE, INVITE, CALLING

    def set_call_id(self, callid):
        self.call_id = callid

    def set_state(self, state):
        pre_state = self.call_state
        self.call_state = state
        if pre_state != self.call_state:
            self.proceed_next_step(state)

    def proceed_next_step(self, state):
        if state == CallState.BYE:
            # sender 와 receiver 모두에게 BYE 를 전송한다..
            data = '''{
                "command": "BYE",
                "contents": {
                    "uuid": "%s",
                    "callid": "%s"
                  }
                }''' % (self.receiver_user.uuid, self.call_id)
            data_json = json.loads(data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(),
                                               self.receiver_user.socket_info)

            data = '''{
                "command": "BYE",
                "contents": {
                    "uuid": "%s",
                    "callid": "%s"
                  }
                }''' % (self.sender_user.uuid, self.call_id)
            data_json = json.loads(data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(),
                                               self.sender_user.socket_info)

            self.sender_user.set_state(CallState.IDLE)
            self.receiver_user.set_state(CallState.IDLE)

        elif state == CallState.INVITE:
            data = '''{
                "command": "INVITE",
                "contents": {
                    "uuid": "%s",
                    "email": "%s",
                    "callid": "%s"
                  }
                }''' % (self.receiver_user.uuid, self.sender_user.email, self.call_id)
            data_json = json.loads(data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(),
                                               self.receiver_user.socket_info)

            self.sender_user.set_state(CallState.INVITE)
            self.receiver_user.set_state(CallState.INVITE)

        elif state == CallState.CANCEL:
            # sender 에게 CANCEL 을 전송한다..
            data = '''{
                            "command": "CANCEL",
                            "response": "REJECT",
                            "contents": {
                                "uuid": "%s",
                                "callid": "%s"
                              }
                            }''' % (self.sender_user.uuid, self.call_id)
            data_json = json.loads(data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(),
                                               self.sender_user.socket_info)

            self.sender_user.set_state(CallState.IDLE)
            self.receiver_user.set_state(CallState.IDLE)

        elif state == CallState.ACCEPT:
            data = '''{
                "command": "ACCEPT",
                "contents": {
                    "uuid": "%s",
                    "callid": "%s"
                  }
                }''' % (self.sender_user.uuid, self.call_id)
            data_json = json.loads(data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(),
                                               self.sender_user.socket_info)

            self.sender_user.set_state(CallState.CALLING)
            self.receiver_user.set_state(CallState.CALLING)

        elif state == CallState.CALLING:
            pass
