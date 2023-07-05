from copy import deepcopy
from unittest import TestCase

from services.storage.mysql_service import MySQLService
from services.storage.sqlite_service import SQLiteService
from services.storage_manager import StorageManager


class StorageManagerTest(TestCase):

    def setUp(self) -> None:
        # service = MySQLService()
        service = SQLiteService("../../sqlite/studio_project.db")
        self.manager = StorageManager(service)
        self.manager.connect()

    def tearDown(self) -> None:
        self.manager.disconnect()

    def test_get_user_when_normal(self):
        # given
        uuid = "user_01"
        # when
        user = self.manager.get_user(uuid)
        # then
        self.assertIsNotNone(user)
        self.assertEqual(user.uuid, uuid)

    def test_update_user_when_firstname_changed(self):
        # given
        uuid = "user_01"
        old_user = self.manager.get_user(uuid)
        mod_user = deepcopy(old_user)
        mod_user.firstname = "Test"
        # when
        self.manager.update_user(user=mod_user)
        # then
        new_user = self.manager.get_user(uuid)
        self.assertEqual(new_user.firstname, mod_user.firstname)
        self.manager.update_user(user=old_user)

    def test_update_user_info_when_status_changed(self):
        # given
        uuid = "user_01"
        item = "status"
        user = self.manager.get_user(uuid)
        status = 0 if user.status else 1
        # when
        self.manager.update_user_info(uuid=uuid, key=item, value=status)
        # then
        user = self.manager.get_user(uuid)
        self.assertEqual(user.status, status)

    def test_update_user_info_when_ip_changed(self):
        # given
        uuid = "user_01"
        key = "ip"
        value = "0.0.0.0"
        old_user = self.manager.get_user(uuid)
        # when
        self.manager.update_user_info(uuid=uuid, key=key, value=value)
        # then
        new_user = self.manager.get_user(uuid)
        self.assertEqual(new_user.ip, value)
        self.manager.update_user_info(uuid=uuid, key=key, value=old_user.ip)
