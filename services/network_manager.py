from abc import ABCMeta, abstractmethod
from enum import Enum

from model.directory_singleton import directory_service
from model.callbroker import callbroker_service
from services.ievent_receiver import IEventReceiver, EventType, UDPPayload, TCPPayload
from services.network.inetwork_service import INetworkService
from services.network.tcp_service import TCPService
from services.network.udp_service import UDPService
from utils.call_state import CallState
import threading
from typing import List, Tuple


class ProtocolType(str, Enum):
    TCP = 'tcp'
    UDP = 'udp'


class NetworkManager:
    tcp_services: List[INetworkService] = []
    udp_services: List[INetworkService] = []
    tcp_ports: list
    udp_ports: list
    client_sockets: list

    tcp_subscriber: List[Tuple[int, IEventReceiver]] = list()
    udp_subscriber: List[Tuple[int, IEventReceiver]] = list()

    @classmethod
    def init(cls, tcp_ports: list = None, udp_ports: list = None):
        cls.tcp_ports = tcp_ports
        cls.udp_ports = udp_ports
        cls.client_sockets = list()

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
            if subscriber[0] == port:
                payload = UDPPayload(sender_ip=address, receive_port=port, packet=data)
                subscriber[1].receive(EventType.UDP_DATA_RECEIVED, payload)

    @classmethod
    def handle_client_connected(cls, event_name, client_socket):
        if event_name == EventType.CLIENT_CONNECTED:
            cls.client_sockets.append(client_socket)
            print(f"append handle_client_connected {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}")
            for subscriber in cls.tcp_subscriber:
                host, port = client_socket.getpeername()
                if subscriber[0] == port:
                    payload = TCPPayload(socket=client_socket)
                    subscriber[1].receive(event_name, payload)
        if event_name == EventType.CLIENT_DISCONNECTED:
            cls.client_sockets.remove(client_socket)
            _, user = directory_service.search_by_socket(client_socket)
            ret, room = callbroker_service.search_by_user(user)
            if ret:
                room.set_state(CallState.BYE)

            directory_service.remove_by_socketinfo(socket_info=client_socket)

    @classmethod
    def get_tcp_services(cls):
        return cls.tcp_services

    @classmethod
    def subscribe(cls, subscriber: IEventReceiver, ptype: ProtocolType, port: int):
        if ptype == ProtocolType.TCP:
            cls.tcp_subscriber.append((port, subscriber))
        if ptype == ProtocolType.UDP:
            cls.udp_subscriber.append((port, subscriber))
