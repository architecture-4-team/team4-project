from typing import List

from services.ievent_receiver import IEventReceiver, RoomPayload, EventType
from utils.call_state import CallState


class ConferenceCallBrokerSingleton:
    room_id: int = 1
    conference_rooms = list()
    subscribers: List[IEventReceiver] = list()

    def __init__(self):
        pass

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

    def state_changed(self, room_id, state, user=None):
        event = EventType.CONF_STATE_CHANGED
        if user:
            if state == CallState.CALLING:
                event = EventType.CONF_USER_JOINED
            elif state == CallState.IDLE:
                event = EventType.CONF_USER_LEAVED
        room = [room for room in self.conference_rooms if room == room_id]
        if room:
            for subscriber in self.subscribers:
                payload = RoomPayload(room=room, state=state, user=user)
                subscriber.receive(event, payload)

    def subscribe(self, subscriber: IEventReceiver):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber: IEventReceiver):
        self.subscribers.append(subscriber)


conferencecallbroker = ConferenceCallBrokerSingleton()
