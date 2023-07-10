from model.conferenceroom import ConferenceRoom


class ConferenceCallBrokerSingleton:
    room_id: int = 1

    def __init__(self):
        self.conference_rooms: ConferenceRoom = []

    def append(self, conf_room_object):
        self.conference_rooms.append(conf_room_object)

    def remove(self, conf_room_object):
        return self.conference_rooms.remove(conf_room_object)

    def make_room_id(self):
        ConferenceCallBrokerSingleton.room_id = ConferenceCallBrokerSingleton.room_id + 1
        return ConferenceCallBrokerSingleton.room_id

    def search_by_roomid(self, room_id):
        for room in self.conference_rooms:
            if room.room_id == room_id:
                return True, room
        return False, None

    def print_info(self):
        for room in self.conference_rooms:
            print('*****************************************')
            print(f'room id : {room.room_id}')
            print(f'participants : {room.get_participants_number()}')
            print(f'participated : ')
            print(f'\t\t{room.print_users_call_states()}')
            print('*****************************************')


conferencecallbroker = ConferenceCallBrokerSingleton()
