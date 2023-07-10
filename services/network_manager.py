from abc import ABCMeta, abstractmethod
from enum import Enum

from services.network.inetwork_service import INetworkService
from services.network.tcp_service import TCPService
from services.network.udp_service import UDPService
import threading
from typing import List, Tuple


class EventType(str, Enum):
    DATA_RECEIVED = 'data-received'
    CLIENT_CONNECTED = 'client-connected'
    CLIENT_DISCONNECTED = 'client-disconnected'


class INetworkEventReceiver(metaclass=ABCMeta):
    @abstractmethod
    def receive_tcp(self, socket, event):
        pass

    @abstractmethod
    def receive_udp(self, data, sender_ip, rcv_port):
        pass


class NetworkManager:
    tcp_services: List[INetworkService] = []
    udp_services: List[INetworkService] = []
    tcp_ports: list
    udp_ports: list
    client_sockets: list

    tcp_subscriber: List[Tuple[int, EventType, INetworkEventReceiver]] = list()
    udp_subscriber: List[Tuple[int, EventType, INetworkEventReceiver]] = list()

    @classmethod
    def init(cls, tcp_ports: list = None, udp_ports: list = None):
        cls.tcp_ports = tcp_ports
        cls.udp_ports = udp_ports
        cls.client_sockets = []

    @classmethod
    def start_network_services(cls):
        tcp_threads = []

        # TCP 서비스 생성
        for tcp_port in cls.tcp_ports:
            tcp_service = TCPService(tcp_port)
            cls.tcp_services.append(tcp_service)
            tcp_service.set_client_socketinfo_callback(cls.handle_client_connected)

        # UDP 서비스 생성
        for udp_port in cls.udp_ports:
            udp_service = UDPService(udp_port)
            cls.udp_services.append(udp_service)
            udp_service.set_receive_callback(cls.receive_udp_data)

        # TCP 서비스 시작
        for tcp_service in cls.tcp_services:
            tcp_thread = threading.Thread(target=tcp_service.start)
            tcp_threads.append(tcp_thread)
            tcp_thread.daemon = True
            tcp_thread.start()

        # UDP 서비스 시작
        udp_threads = []
        for udp_service in cls.udp_services:
            udp_thread = threading.Thread(target=udp_service.start)
            udp_threads.append(udp_thread)
            udp_thread.daemon = True
            udp_thread.start()

    @classmethod
    def stop_network_services(cls):
        for tcp_service in cls.tcp_services:
            tcp_service.stop()

        for udp_service in cls.udp_services:
            udp_service.stop()

    @classmethod
    def send_tcp_data(cls, data, client_socket):
        # client_socket.sendall(data)
        for tcp_service in cls.tcp_services:
            if isinstance(tcp_service, TCPService):
                tcp_service.sendto(data, client_socket)

    @classmethod
    def receive_tcp_data(cls):
        # return self.tcp_service.receive()
        pass

    @classmethod
    def send_udp_data(cls, data, address):
        # self.udp_service.send(data)
        for udp_service in cls.udp_services:
            if isinstance(udp_service, UDPService):
                udp_service.sendto(data, address)

    @classmethod
    def receive_udp_data(cls, data, address, port):
        for subscriber in cls.udp_subscriber:
            if subscriber[0] == port and subscriber[1] == EventType.DATA_RECEIVED:
                subscriber[2].receive_udp(data, address, port)

    @classmethod
    def handle_client_connected(cls, client_socket):
        cls.client_sockets.append(client_socket)
        print(f"append handle_client_connected {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}")
        for subscriber in cls.tcp_subscriber:
            if subscriber[1] == EventType.CLIENT_CONNECTED or subscriber[1] == EventType.CLIENT_DISCONNECTED:
                subscriber[2].receive_tcp(client_socket, subscriber[1])

    @classmethod
    def get_tcp_services(cls):
        return cls.tcp_services

    @classmethod
    def subscribe_tcp(cls, port: int, event: EventType, subscriber: INetworkEventReceiver):
        cls.tcp_subscriber.append((port, event, subscriber))

    @classmethod
    def subscribe_udp(cls, port: int, event: EventType, subscriber: INetworkEventReceiver):
        cls.udp_subscriber.append((port, event, subscriber))
