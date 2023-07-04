from services.storage.istorage_service import IStorageService


class StorageManager:
    def __init__(self, storage_service: IStorageService):
        self.storage_service = storage_service

    def connect_to_database(self):
        self.storage_service.connect()

    def disconnect_from_database(self):
        self.storage_service.disconnect()

    def execute_query(self, query):
        return self.storage_service.execute_query(query)
