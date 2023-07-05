import mysql.connector
from services.storage.istorage_service import IStorageService


class MySQLService(IStorageService):
    def connect(self):
        # MySQL 데이터베이스에 연결하는 로직
        pass

    def disconnect(self):
        # MySQL 데이터베이스 연결 해제하는 로직
        pass

    def execute_query(self, query):
        # MySQL 쿼리 실행하는 로직
        pass

    def execute_select_query(self, query):
        pass

    def update_record(self, table, record_id, data):
        pass
