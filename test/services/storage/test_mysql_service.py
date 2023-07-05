from unittest import TestCase

from services.storage.mysql_service import MySQLService


class MySQLServiceTest(TestCase):

    def setUp(self) -> None:
        self.service = MySQLService()
        self.service.connect()

    def tearDown(self) -> None:
        self.service.disconnect()

    def test_create_and_delete_record_when_normal(self):
        # given
        table = 'user_table'
        data = {
            "uuid": "user_05",
            "contact_id": "test5@lge.com",
            "email": "test5@lge.com",
            "password": "qwerty",
            "firstname": "Gildong",
            "lastname": "Hong",
            "ip": "192.168.2.8",
            "status": 1,
            "summary": "test5@lge.com Gildong Hong",
        }
        # when
        self.service.create_record(table, data)
        # then
        rows = self.service.read_records(table, {"uuid": "user_05"})
        self.assertEqual(rows[0][0], data["uuid"])

        self.service.delete_record(table, {"uuid": "user_05"})

    def test_read_record_when_get_one_row(self):
        # given
        table = 'user_table'
        condition = {
            "uuid": "user_01"
        }
        # when
        rows = self.service.read_records(table=table, condition=condition)
        # then
        self.assertEqual(rows[0][0], condition["uuid"])

    def test_read_record_when_get_rows(self):
        # given
        table = 'user_table'
        condition = {
            "*": "*"
        }
        # when
        rows = self.service.read_records(table=table, condition=condition)
        # then
        self.assertGreater(len(rows), 1)

    def test_update_record_when_status_is_diabled(self):
        # given
        table = 'user_table'
        condition = {
            "uuid": "user_01"
        }
        data = {
            "status": 1
        }
        # when
        self.service.update_record(table=table, condition=condition, data=data)
        # then
        rows = self.service.read_records(table=table, condition=condition)
        print(rows[0])
        self.assertEqual(rows[0][7], 1)
