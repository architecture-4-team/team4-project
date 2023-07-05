from abc import ABC, abstractmethod


class IStorageService(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def create_record(self, table, data: dict):
        pass

    @abstractmethod
    def read_records(self, table, condition: dict):
        pass

    @abstractmethod
    def update_records(self, table, condition: dict, data: dict):
        pass

    @abstractmethod
    def delete_records(self, table, condition: dict):
        pass
