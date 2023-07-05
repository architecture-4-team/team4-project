from unittest import TestCase

from services.storage.sqlite_service import SQLiteService


class SQLiteServiceTest(TestCase):

    def setUp(self) -> None:
        self.service = SQLiteService("../../../sqlite/studio_project.db")
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
            "pwd": "qwerty",
            "firstname": "Gildong",
            "lastname": "Hong",
            "ip": "192.168.2.8",
            "status": 1,
            "summary": "test5@lge.com Gildong Hong",
            "question1": "a1",
            "question2": "a2",
            "question3": "a3",
        }
        # when
        self.service.create_record(table, data)
        # then
        rows = self.service.read_records(table, {"uuid": "user_05"})
        self.assertEqual(rows[0][0], data["uuid"])

        self.service.delete_records(table, {"uuid": "user_05"})

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

    def test_update_record_when_status_is_changed(self):
        # given
        table = 'user_table'
        condition = {
            "uuid": "user_01"
        }
        rows = self.service.read_records(table=table, condition=condition)
        status = 0 if rows[0][7] else 1
        data = {
            "status": status
        }
        # when
        self.service.update_records(table=table, condition=condition, data=data)
        # then
        rows = self.service.read_records(table=table, condition=condition)
        print(rows[0])
        self.assertEqual(rows[0][7], status)

    def test_delete_records_when_normal(self):
        # given
        table = 'user_table'
        condition = {
            "uuid": "user_05"
        }
        # when
        self.service.delete_records(table=table, condition=condition)
        # then
        rows = self.service.read_records(table=table, condition=condition)
        self.assertEqual(len(rows), 0)
