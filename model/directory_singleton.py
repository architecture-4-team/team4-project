from model.user import UserExt


class DirectorySingleton:
    def __init__(self):
        self.users: UserExt = []

    def append(self, user_object):
        return self.users.append(user_object)

    def remove(self, user_object):
        return self.users.remove(user_object)

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


directory_service = DirectorySingleton()