import json
from PyQt5.QtCore import QObject, pyqtSignal
from model.login import Login


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
        # test
        # self.network_manager.send_tcp_data(data, client_socket)
        #
        # 수신한 데이터 파싱 (별도의 롤 분리 필요, signal/slot 구조로 연결? )
        try:
            payload = json.loads(data.decode())
            print('command:', payload['command'])
        except json.JSONDecodeError:
            print('Invalid JSON format')
            pass

        # 프로토콜 parsing 을 위해 분리 필요!!
        # if payload['command'] == 'LOGIN': # 로그인인 경우 ( ) -> Login 객체로 이벤트 전달
        #     print(f'contents :', payload['contents']['email'], payload['contents']['password'])
        #
        #     # signal/slot 을 사용하는 방법
        #     # self.signal_login.emit(data.decode(), client_socket)
        #
        #     # static method 를 사용하는 방법
        #     return_value, user_uuid = Login.do_process(email=payload['contents']['email'], password=payload['contents']['password'])
        #     print(f'<-- Login : {return_value}, {user_uuid}')
        #     # response 에 대한 json 생성 필요
        #     if return_value:
        #         ret_data = f'''{{
        #                 "command": "LOGIN",
        #                 "response": "OK",
        #                 "contents": {{
        #                     "uuid": "{user_uuid}",
        #                   }},
        #                 }}'''
        #         print(ret_data)
        #         ret_data_json = json.dumps(ret_data)
        #         self.network_manager.send_tcp_data(ret_data_json.encode(), client_socket)
        #     else:
        #         ret_data = f'''{{
        #                 "command": "LOGIN",
        #                 "response": "NOT_OK",
        #                 "contents": {{
        #                     "reason": "NOT REGISTERED"
        #                   }},
        #                 }}'''
        #         ret_data_json = json.dumps(ret_data)
        #         self.network_manager.send_tcp_data(ret_data_json.encode(), client_socket)

        # call -> callbroker 로 이벤트 전달

    def handle_udp_data(self, data, address):
        # UDP 데이터 수신 이벤트 처리 로직
        print(f"UDPService: Received data from {address[0]}:{address[1]}: {data.decode()}")
        # self.network_manager.send_udp_data(data, address)
