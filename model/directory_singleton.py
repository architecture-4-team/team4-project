from typing import List

from model.user import UserExt
from services.ievent_receiver import IEventReceiver, EventType, UserPayload


class DirectorySingleton:
    users: List[UserExt] = list()
    subscribers: List[IEventReceiver] = list()

    def __init__(self):
        pass

    def append(self, user_object):
        for user in self.users: # 방어코드( 동일한 유저가 2번이상 SESSION 을 요청하는 경우 )
            if user == user_object:
                print('user is already in directory!!')
                return

        for subscriber in self.subscribers:
            payload = UserPayload(user=user_object)
            subscriber.receive(EventType.USER_ADDED, payload)

        return self.users.append(user_object)

    def remove(self, user_object):
        for subscriber in self.subscribers:
            payload = UserPayload(user=user_object)
            subscriber.receive(EventType.USER_REMOVED, payload)
        return self.users.remove(user_object)

    def remove_by_socketinfo(self, socket_info):
        for user in self.users:
            if user.socket_info == socket_info:
                self.users.remove(user)

    def search_by_email(self, email):
        for user in self.users:
            if user.email == email:
                return True, user
        return False, None

    def search_by_contactid(self, contact_id):
        for user in self.users:
            if user.contact_id == contact_id:
                return True, user
        return False, None

    def search_by_socket(self, socket):
        for user in self.users:
            if user.socket_info == socket:
                return True, user

        return False, None

    def search_by_uuid(self, uuid):
        for user in self.users:
            if str(user.uuid) == uuid:
                return True, user
        return False, None

    def print_info(self):
        for user in self.users:
            print('************************************')
            print(f'user email : {user.email}')
            print(f'user contact id : {user.contact_id}')
            print(f'user socket info : {user.socket_info.getpeername()[0]}')
            print(f'user uuid : {user.uuid}')
            print(f'user name : {user.firstname, user.lastname}')
            print('************************************')

    def subscribe(self, subscriber: IEventReceiver):
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber: IEventReceiver):
        self.subscribers.remove(subscriber)


directory_service = DirectorySingleton()
