# services/network_service.py
from abc import abstractmethod, ABCMeta


class INetworkService(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, port: int):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def receive(self):
        pass
