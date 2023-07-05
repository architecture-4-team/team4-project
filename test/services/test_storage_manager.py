from unittest import TestCase

from services.storage.mysql_service import MySQLService
from services.storage_manager import StorageManager


class StorageManagerTest(TestCase):
    def setUp(self) -> None:
        service = MySQLService()
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

    def test_update_user_info_when_normal(self):
        # given
        uuid = "user_01"
        item = "status"
        user = self.manager.get_user(uuid)
        status = 0 if user.status else 1
        # when
        ret = self.manager.update_user_info(uuid=uuid, key=item, value=status)
        # then
        self.assertEqual(ret, True)
