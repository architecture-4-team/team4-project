import pymysql
from pymysql.cursors import DictCursor

from services.storage.istorage_service import IStorageService


class MySQLService(IStorageService):

    conn = None
    PLACE_HOLDER = '%s'

    def connect(self):
        self.conn = pymysql.connect(host='localhost', user='team4', password='fantastic4', database='studio_project')

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_record(self, table, data: dict):
        keys = ",".join(list(data.keys()))
        values = tuple(data.values())
        values_statement = ','.join([f'{self.PLACE_HOLDER}' for value in list(data.values())])

        with self.conn.cursor() as cursor:
            query = f"INSERT INTO {table}({keys}) VALUES({values_statement})"
            print(query)
            cursor.execute(query, values)
            self.conn.commit()

    def read_records(self, table: str, condition: dict):
        where_statement = ""
        if not condition.get("*"):
            where_statement = f" WHERE {self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)}"
        values = tuple(condition.values())
        with self.conn.cursor(DictCursor) as cursor:
            query = f"SELECT * FROM {table}{where_statement}"
            if where_statement:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            result = cursor.fetchall()

            return result

    def update_records(self, table, condition: dict, data: dict):
        where_statement = self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)
        cond_values = list(condition.values())
        statement = [f"{k}={self.PLACE_HOLDER}" for k, v in data.items()]
        statement = ','.join(statement)
        values = list(data.values())
        values.extend(cond_values)
        with self.conn.cursor() as cursor:
            query = f"UPDATE {table} SET {statement} WHERE {where_statement}"
            print(query)
            affected_rows = cursor.execute(query, tuple(values))
            self.conn.commit()

            return affected_rows

    def delete_records(self, table, condition: dict):
        where_statement = self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)
        values = tuple(condition.values())
        with self.conn.cursor() as cursor:
            query = f"DELETE FROM {table} WHERE {where_statement}"
            cursor.execute(query, values)
            self.conn.commit()

    @staticmethod
    def _get_where_statement(keys, place_holder) -> str:
        return ' AND '.join([f'{key}={place_holder}' for key in keys])
