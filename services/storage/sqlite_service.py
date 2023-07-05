import os.path
import sqlite3

from services.storage.mysql_service import MySQLService


class SQLiteService(MySQLService):

    conn = None
    db_path: str
    PLACE_HOLDER = '?'

    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        if os.path.exists(self.db_path):
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        else:
            print('Database file does not exist.')

    def disconnect(self):
        self.conn.close()

    def create_record(self, table, data: dict):
        keys = ",".join(list(data.keys()))
        values = tuple(data.values())
        values_statement = ','.join([f'{self.PLACE_HOLDER}' for value in list(data.values())])

        cursor = self.conn.cursor()
        query = f"INSERT INTO {table}({keys}) VALUES({values_statement})"
        print(query)
        cursor.execute(query, values)
        self.conn.commit()
        cursor.close()

    def read_records(self, table, condition: dict):
        where_statement = ""
        if not condition.get("*"):
            where_statement = f" WHERE {self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)}"
        values = tuple(condition.values())
        cursor = self.conn.cursor()
        query = f"SELECT * FROM {table}{where_statement}"
        if where_statement:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        return result

    def update_records(self, table, condition: dict, data: dict):
        where_statement = self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)
        cond_values = list(condition.values())
        statement = [f"{k}={self.PLACE_HOLDER}" for k, v in data.items()]
        statement = ','.join(statement)
        values = list(data.values())
        values.extend(cond_values)

        cursor = self.conn.cursor()
        query = f"UPDATE {table} SET {statement} WHERE {where_statement}"
        cursor.execute(query, tuple(values))
        self.conn.commit()
        cursor.close()

    def delete_records(self, table, condition: dict):
        where_statement = self._get_where_statement(list(condition.keys()), self.PLACE_HOLDER)
        values = tuple(condition.values())
        cursor = self.conn.cursor()
        query = f"DELETE FROM {table} WHERE {where_statement}"
        cursor.execute(query, values)
        self.conn.commit()
