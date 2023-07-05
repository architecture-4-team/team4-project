from abc import ABC, abstractmethod


class IStorageService(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

    @abstractmethod
    def execute_select_query(self, query):
        pass

    # REST 서비스에서 담당
    # @abstractmethod
    # def create_record(self, table, data):
    #     pass
    #
    # @abstractmethod
    # def read_records(self, table):
    #     pass

    @abstractmethod
    def delete_record(self, table, record_id):
        pass

    @abstractmethod
    def update_record(self, table, record_id, data):
        pass
