from typing import Optional

from model.user import User
from services.storage.istorage_service import IStorageService


class StorageManager:
    def __init__(self, storage_service: IStorageService):
        self.storage_service = storage_service

    def connect(self):
        self.storage_service.connect()

    def disconnect(self):
        self.storage_service.disconnect()

    def get_user(self, uuid) -> Optional[User]:
        rows = self.storage_service.read_records("user_table", {"uuid": uuid})
        if len(rows) > 0:
            return User(**rows[0])
        return None

    def update_user_info(self, uuid, key, value) -> bool:
        affected_rows = self.storage_service.update_records("user_table", {"uuid": uuid}, {key: value})
        if affected_rows > 0:
            return True
        return False
