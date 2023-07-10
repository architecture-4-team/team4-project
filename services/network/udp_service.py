import socket
from services.network.inetwork_service import INetworkService


class UDPService(INetworkService):

    DEFAULT_BUF_SIZE = 50 * 1024    # for gstreamer

    def __init__(self, port: int):
        self.address = None
        self.port = port
        self.socket = None
        self.is_listening = False
        self.receive_callback = None
        print('UDPService : port number ->', port)

    def start(self):
        # UDP 서비스 시작 로직
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.is_listening = True
        print(f'UDPService started listening on port {self.port}')
        self.receive()

    def stop(self):
        # UDP 서비스 종료 로직
        self.is_listening = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print(f'UDP stop : {self.port}')

    def send(self, data):
        # 데이터 전송 로직
        self.socket.sendto(data, self.address)

    def sendto(self, data, address):
        self.socket.sendto(data, address)

    def receive(self):
        # 데이터 수신 로직
        while self.is_listening and self.socket:
            data, self.address = self.socket.recvfrom(self.DEFAULT_BUF_SIZE)
            print(self.address)
            if self.receive_callback:
                self.receive_callback(data, self.address[0], self.port)

    def set_receive_callback(self, callback):
        self.receive_callback = callback
