from PyQt5.QtCore import QObject, pyqtSignal


class NetworkController(QObject):
    signal_login = pyqtSignal(str, object)

    def __init__(self, network_manager):
        super().__init__()
        self.network_manager = network_manager
        self.network_manager.start_network_services()

        # TCPService의 데이터 수신 이벤트에 대한 콜백 등록
        for tcp_service in self.network_manager.tcp_services:
            tcp_service.set_receive_callback(self.handle_tcp_data)

        # UDPService의 데이터 수신 이벤트에 대한 콜백 등록
        for udp_service in self.network_manager.udp_services:
            udp_service.set_receive_callback(self.handle_udp_data)

    def handle_tcp_data(self, data, client_socket):
        # 데이터 수신 이벤트 처리 로직
        print(f"TCPService: Received data from client {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}: {data.decode()}")
        # self.network_manager.send_tcp_data(data, client_socket)
        # 수신한 데이터 파싱 (별도의 롤 분리 필요, signal/slot 구조로 연결? )

        # 로그인인 경우 ( ) -> Login 객체로 이벤트 전달
        self.signal_login.emit(data.decode(), client_socket)

        # call -> callbroker 로 이벤트 전달

    def handle_udp_data(self, data, address):
        # UDP 데이터 수신 이벤트 처리 로직
        print(f"UDPService: Received data from {address[0]}:{address[1]}: {data.decode()}")
        # self.network_manager.send_udp_data(data, address)
