class ConferenceCallBrokerSingleton:
    room_id: int = 1

    def __init__(self):
        self.conference_rooms = []

    def append(self, conf_room_object):
        self.conference_rooms.append(conf_room_object)

    def remove(self, conf_room_object):
        return self.conference_rooms.remove(conf_room_object)

    def make_room_id(self):
        ConferenceCallBrokerSingleton.room_id = ConferenceCallBrokerSingleton.room_id + 1
        return ConferenceCallBrokerSingleton.room_id

    def search_by_roomid(self, room_id):
        for room in self.conference_rooms:
            if room.id == room_id:
                return True, room
        return False, None


conferencecallbroker = ConferenceCallBrokerSingleton()
