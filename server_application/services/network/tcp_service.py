from abc import ABC
from services.network.inetwork_service import INetworkService
import socket
import threading


class TCPService(INetworkService, ABC):
    def __init__(self, port: int):
        super().__init__(port)
        self.port = port
        self.server_socket = None
        self.client_sockets = []
        self.is_listening = False
        self.receive_callback = None
        self.client_socketinfo_callback = None
        print('TCPService : port number ->', port)

    def start(self):
        print(f'TCP start : {self.port}')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.bind(('localhost', self.port))
        self.server_socket.bind(('192.168.56.103', self.port))
        self.server_socket.listen(1)
        self.is_listening = True
        self.accept_connections()

    def accept_connections(self):
        while self.is_listening:
            client_socket, client_address = self.server_socket.accept()
            print(f'Accepted connection from {client_address}')
            # self.client_sockets.append(client_socket)
            self.notify_client_connected(client_socket, connected=True)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.setDaemon(True)
            client_thread.start()

    def stop(self):
        # TCP 서비스 종료 로직
        print(f'TCP stop : {self.port}')
        self.is_listening = False
        if self.server_socket:
            self.server_socket.close()

    def send(self, data):
        # 데이터 전송 로직
        # client_socket.sendall(data)
        # print('send')
        pass

    def sendto(self, data, client_socket):
        client_socket.sendall(data)
        print(f'send : {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}: {data.decode()}')

    def receive(self):
        pass

    def handle_client(self, client_socket):
        # 데이터 수신 로직
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                if self.receive_callback:
                    self.receive_callback(data, client_socket)
                # print(f"TCPService: Received data from client {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}: {data.decode()}")
                # client_socket.sendall(data)
        except Exception as e:
            print(f"TCPService: Error occurred while handling client: {e}")
        finally:
            client_socket.close()
            print("TCPService: Client connection closed")
            self.notify_client_connected(client_socket, connected=False)
        print('receive')

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def set_client_socketinfo_callback(self, callback):
        self.client_socketinfo_callback = callback

    def notify_client_connected(self, client_socket, connected):
        if self.client_socketinfo_callback:
            self.client_socketinfo_callback(client_socket, connected)
        else:
            print('No client callback registered')
