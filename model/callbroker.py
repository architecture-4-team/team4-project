class CallBrokerSingleton:
    call_id: int = 1

    def __init__(self):
        self.call_rooms = []

    def append(self, callroom_object):
        self.call_rooms.append(callroom_object)

    def remove(self, callroom_object):
        return self.call_rooms.remove(callroom_object)

    def make_call_id(self):
        CallBrokerSingleton.call_id = CallBrokerSingleton.call_id + 1;
        return CallBrokerSingleton.call_id

    def search_by_callid(self, callid):
        for call_room in self.call_rooms:
            if call_room.call_id == callid:
                return True, call_room
        return False, None

    def search_by_user(self, user):
        for call_room in self.call_rooms:
            if call_room.sender_user.socket_info == user.socket_info:
                return True, call_room
        return False, None

    def print_info(self):
        for room in self.call_rooms:
            print('************************************')
            print(f'room no : {room.call_id}')
            print('************************************')


callbroker_service = CallBrokerSingleton()
