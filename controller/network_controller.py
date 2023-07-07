from PyQt5.QtCore import QObject, pyqtSignal
import json
from PyQt5.QtCore import QObject, pyqtSignal
from model.login import Login
from model.logout import LogOut
from model.callbroker import callbroker_service
from model.callroom import CallRoom
from model.directory_singleton import directory_service
from utils.call_state import CallState


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
        print(
            f"TCPService: Received data from client {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}: {data.decode()}")
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
        if payload['command'] == 'LOGIN':  # 로그인인 경우 ( ) -> Login 객체로 이벤트 전달
            print(f'contents :', payload['contents']['email'], payload['contents']['password'])

            # signal/slot 을 사용하는 방법
            # self.signal_login.emit(data.decode(), client_socket)

            # static method 를 사용하는 방법
            return_value, user_uuid = Login.do_process(email=payload['contents']['email'],
                                                       password=payload['contents']['password'],
                                                       socket=client_socket)
            print(f'<-- Login : {return_value}, {user_uuid}')
            # response 에 대한 json 생성 필요
            if return_value:
                ret_data = '''{
                    "command": "LOGIN",
                    "response": "OK",
                    "contents": {
                        "uuid": "%s"
                      }
                    }''' % user_uuid
                print(ret_data)
                data_json = json.loads(ret_data)
                ret_data_json = json.dumps(data_json)
                self.network_manager.send_tcp_data(ret_data_json.encode(), client_socket)
            else:
                ret_data = f'''{{
                        "command": "LOGIN",
                        "response": "NOT_OK",
                        "contents": {{
                            "reason": "NOT REGISTERED"
                          }}
                        }}'''
                data_json = json.loads(ret_data)
                ret_data_json = json.dumps(data_json)
                self.network_manager.send_tcp_data(ret_data_json.encode(), client_socket)
        elif payload['command'] == 'LOGOUT':
            print(f'LOGOUT info :', payload['contents']['uuid'])
            ret, user = LogOut.do_process(uuid=payload['contents']['uuid'])
            ret_data = f'''{{
                "command": "LOGOUT",
                "response": "OK",
                "contents": {{
                    "uuid": "%s"
                  }}
                }}''' % user.uuid
            data_json = json.loads(ret_data)
            ret_data_json = json.dumps(data_json)
            self.network_manager.send_tcp_data(ret_data_json.encode(), client_socket)
            pass
        elif payload['command'] == 'INVITE':  # call -> callbroker 로 이벤트 전달
            # 수신자 online 여부 체크 ( directory 내에 있으면 됨 )
            ret_dst, dst_user = directory_service.search_by_email(payload['contents']['target'])
            ret_snd, snd_user = directory_service.search_by_uuid(payload['contents']['uuid'])
            # 수신자 busy 여부 체크 ( User 객체의 call_state 를 확인 )
            if ret_dst != False and (dst_user.get_state() == CallState.IDLE):
                # CallRoom 을 생성하고 call broker 에 방을 추가한다
                room = CallRoom(snd_user, dst_user, self.network_manager)
                # call_id 는 call broker 에서 받아온다
                room.set_call_id(str(callbroker_service.make_call_id()))
                # state 를 IDLE 에서 INVITE로 변경
                room.set_state(CallState.INVITE)

                callbroker_service.append(room)
                callbroker_service.print_info()
                # ret_data = f'''{{
                #     "command": "CANCEL",
                #     "response": "NOT AVAILABLE",
                #     "contents": {{
                #         "uuid": "%s"
                #       }}
                #     }}''' % snd_user.uuid
                # data_json = json.loads(ret_data)
                # ret_data_json = json.dumps(data_json)
                # self.network_manager.send_tcp_data(ret_data_json.encode(), dst_user.socket_info)
            else:
                # sender 에게 CANCEL 보낸다( NOT AVAILABLE )
                ret_data = ''
                if ret_dst == False:
                    ret_data = f'''{{
                        "command": "CANCEL",
                        "response": "NOT AVAILABLE",
                        "contents": {{
                            "uuid": "%s"
                          }}
                        }}''' % snd_user.uuid
                elif dst_user.get_state() != CallState.IDLE:
                    ret_data = f'''{{
                        "command": "CANCEL",
                        "response": "BUSY",
                        "contents": {{
                            "uuid": "%s"
                          }}
                        }}''' % snd_user.uuid
                data_json = json.loads(ret_data)
                ret_data_json = json.dumps(data_json)
                self.network_manager.send_tcp_data(ret_data_json.encode(), snd_user.socket_info)
                return

        elif payload['command'] == 'ACCEPT':
            # call id 로부터 call room 을 찾는다.
            ret, room = callbroker_service.search_by_callid(payload['contents']['callid'])
            room.set_state(CallState.ACCEPT)

        elif payload['command'] == 'BYE':
            ret, room = callbroker_service.search_by_callid(payload['contents']['callid'])
            # 해당 room 의 call 상태가 CALLING 일때만 가능하도록 예외처리 필요
            room.set_state(CallState.BYE)
            callbroker_service.remove(room)

        elif payload['command'] == 'CANCEL':
            ret, room = callbroker_service.search_by_callid(payload['contents']['callid'])
            # 해당 room 의 call 상태가 INVITE 일때만 가능하도록 예외처리 필요
            room.set_state(CallState.CANCEL)
            callbroker_service.remove(room)

    def handle_udp_data(self, data, address):
        # UDP 데이터 수신 이벤트 처리 로직
        print(f"UDPService: Received data from {address[0]}:{address[1]}: {data.decode()}")
        # self.network_manager.send_udp_data(data, address)
