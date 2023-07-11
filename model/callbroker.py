from typing import List

from services.ievent_receiver import IEventReceiver, RoomPayload, EventType


class CallBrokerSingleton:
    call_id: int = 1
    subscriber: List[IEventReceiver] = list()

    def __init__(self):
        self.call_rooms = []

    def append(self, callroom_object):
        self.call_rooms.append(callroom_object)

    def remove(self, callroom_object):
        return self.call_rooms.remove(callroom_object)

    def make_call_id(self):
        CallBrokerSingleton.call_id = CallBrokerSingleton.call_id + 1
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

    def call_state_changed(self, room_id, state):
        print('call state changed', room_id, state)
        room = [room for room in self.call_rooms if room.call_id == room_id]
        if room:
            for subscriber in self.subscriber:
                payload = RoomPayload(room=room[0], state=state)
                subscriber.receive(EventType.STATE_CHANGED, payload)
        else:
            print('no room')
            for room in self.call_rooms:
                print(room.call_id)

    def subscribe(self, subscriber: IEventReceiver):
        self.subscriber.append(subscriber)

    def unsubscribe(self, subscriber: IEventReceiver):
        self.subscriber.remove(subscriber)


callbroker_service = CallBrokerSingleton()
