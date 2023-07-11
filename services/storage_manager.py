from dataclasses import asdict
from datetime import datetime
from typing import Optional

import pytz

from model.user import UserExt, User
from services.storage.istorage_service import IStorageService
from services.storage.mysql_service import MySQLService


class StorageManager:
    def __init__(self, storage_service: IStorageService):
        self.storage_service = storage_service

    def connect(self):
        self.storage_service.connect()

    def disconnect(self):
        self.storage_service.disconnect()

    def get_user_by_uuid(self, uuid) -> Optional[User]:
        rows = self.storage_service.read_records("user_table", {"uuid": uuid})
        if len(rows) > 0:
            return User(**rows[0])
        return None

    def get_user_by_email(self, email) -> Optional[User]:
        rows = self.storage_service.read_records("user_table", {"email": email})
        if len(rows) > 0:
            return User(**rows[0])
        return None

    def update_user(self, user: User):
        user.updated_at = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.storage_service.update_records("user_table", {"uuid": user.uuid}, asdict(user))

    def update_user_info(self, uuid, key, value):
        self.storage_service.update_records("user_table", {"uuid": uuid}, {key: value})


dbcon = MySQLService()
storage_manager = StorageManager(dbcon)
storage_manager.connect()
