from services.network.inetwork_service import INetworkService
from services.network.tcp_service import TCPService
from services.network.udp_service import UDPService
import threading
from typing import List
from model.directory_singleton import directory_service


class NetworkManager:
    def __init__(self, tcp_ports=None, udp_ports=None):
        self.tcp_services: List[INetworkService] = []
        self.udp_services: List[INetworkService] = []
        self.tcp_ports = tcp_ports
        self.udp_ports = udp_ports
        self.client_sockets = []

    def start_network_services(self):
        tcp_threads = []

        # TCP 서비스 생성
        for tcp_port in self.tcp_ports:
            tcp_service = TCPService(tcp_port)
            self.tcp_services.append(tcp_service)
            tcp_service.set_client_socketinfo_callback(self.handle_client_connected)


        # UDP 서비스 생성
        for udp_port in self.udp_ports:
            udp_service = UDPService(udp_port)
            self.udp_services.append(udp_service)

        # TCP 서비스 시작
        for tcp_service in self.tcp_services:
            tcp_thread = threading.Thread(target=tcp_service.start)
            tcp_threads.append(tcp_thread)
            tcp_thread.setDaemon(True)
            tcp_thread.start()

        # UDP 서비스 시작
        udp_threads = []
        for udp_service in self.udp_services:
            udp_thread = threading.Thread(target=udp_service.start)
            udp_threads.append(udp_thread)
            udp_thread.setDaemon(True)
            udp_thread.start()

    def stop_network_services(self):
        for tcp_service in self.tcp_services:
            tcp_service.stop()

        for udp_service in self.udp_services:
            udp_service.stop()
        pass

    def send_tcp_data(self, data, client_socket):
        # client_socket.sendall(data)
        for tcp_service in self.tcp_services:
            if isinstance(tcp_service, TCPService):
                for cs in self.client_sockets:
                    if client_socket == cs:
                        tcp_service.sendto(data, client_socket)
                # tcp_service.sendto(data, client_socket)

    def receive_tcp_data(self):
        # return self.tcp_service.receive()
        pass

    def send_udp_data(self, data, address):
        # self.udp_service.send(data)
        for udp_service in self.udp_services:
            if isinstance(udp_service, UDPService):
                udp_service.sendto(data, address)

    def receive_udp_data(self):
        # return self.udp_service.receive()
        pass

    def handle_client_connected(self, client_socket, connected):
        if connected:
            self.client_sockets.append(client_socket)
            print(f"append handle_client_connected {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}")
        else:
            self.client_sockets.remove(client_socket)
            ret, user = directory_service.search_by_socket(client_socket)
            if ret:
                directory_service.remove(user)
                directory_service.print_info()
