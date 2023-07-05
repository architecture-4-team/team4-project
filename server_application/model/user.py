class User:
    def __init__(self, email_id, contact_id, uuid, firstname, lastname, socket_info):
        self.email_id = email_id
        self.contact_id = contact_id
        self.uuid = uuid
        self.name = (firstname, lastname)
        self.socket_info = socket_info

