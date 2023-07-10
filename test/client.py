import atexit
import socket
import json
import threading
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


HOST = '192.168.56.103'  # 서버의 IP 주소
PORT = 10000  # 서버의 포트 번호
ID = 'warebowl@hotmail.com'
TARGET_ID = 'abc@gmail.com'
PWD = '12345678'
UUID = ''
callid = ''


# JSON 데이터를 서버로 전송하는 함수
def send_json_data(sock, data):
    json_data = json.dumps(data)  # JSON으로 직렬화
    sock.sendall(json_data.encode())


# JSON 데이터를 수신하는 함수
def receive_json_data(sock):
    json_data = sock.recv(1024).decode()
    print(json_data, type(json_data))
    data = json.loads(json_data)  # JSON 역직렬화
    return data


# 수신 쓰레드에서 실행될 함수
def receive_thread(sock):
    global UUID, callid
    while True:
        try:
            received_data = receive_json_data(sock)
            print('Received data from server:', received_data, type(received_data))
            UUID = received_data['contents']['uuid']
            print(UUID)

            if "callid" in received_data['contents']:
                callid = received_data['contents']['callid']
                print(callid)

        except json.JSONDecodeError:
            print('recv Invalid JSON format')
            break
        except ConnectionError:
            print('Disconnected from server')
            break


# TCP 소켓 생성
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 연결
sock.connect((HOST, PORT))
print('Connected to server')

# 수신을 위한 쓰레드 시작
receive_thread = threading.Thread(target=receive_thread, args=(sock,), daemon=True)
# receive_thread.setDaemon(True)
receive_thread.start()

# # 사용자로부터 JSON 데이터 입력 받아 서버로 전송
# while True:
#     input_data = input('Enter JSON data to send (or "quit" to exit): ')
#     if input_data == 'quit':
#         break
#     try:
#         json_data = json.loads(input_data)  # JSON 파싱
#         send_json_data(sock, json_data)
#     except json.JSONDecodeError:
#         print('Invalid JSON format')


def cleanup():
    # 연결 종료
    sock.close()

    # Perform other cleanup tasks
    print("Performing cleanup...")


atexit.register(cleanup)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Button Example')
        self.resize(300, 400)

        # 버튼 생성 및 설정
        self.button1 = QPushButton('Login', self)
        self.button1.clicked.connect(self.button1_clicked)
        self.button1.setGeometry(50, 50, 100, 30)

        self.button2 = QPushButton('Logout', self)
        self.button2.clicked.connect(self.button2_clicked)
        self.button2.setGeometry(50, 100, 100, 30)


        self.button3 = QPushButton('INVITE', self)
        self.button3.clicked.connect(self.button3_clicked)
        self.button3.setGeometry(50, 150, 100, 30)


        self.button4 = QPushButton('ACCEPT', self)
        self.button4.clicked.connect(self.button4_clicked)
        self.button4.setGeometry(50, 200, 100, 30)


        self.button5 = QPushButton('CANCEL', self)
        self.button5.clicked.connect(self.button5_clicked)
        self.button5.setGeometry(50, 250, 100, 30)


        self.button6 = QPushButton('BYE', self)
        self.button6.clicked.connect(self.button6_clicked)
        self.button6.setGeometry(50, 300, 100, 30)


        # 추가 버튼 생성
        # self.additional_buttons = []
        # for i in range(3, 11):
        #     button = QPushButton(f'Button {i}', self)
        #     button.clicked.connect(lambda _, num=i: self.additional_button_clicked(num))
        #     button.setGeometry(50, 150 + (i-3) * 50, 100, 30)
        #     self.additional_buttons.append(button)

    def button1_clicked(self):
        global ID
        global PWD
        print('**** LOGIN ****')
        # 버튼 1을 클릭했을 때 실행할 코드를 여기에 추가
        # data = '''{
        #         "command": "LOGIN",
        #         "contents": {
        #             "email": "warebowl@gmail.com",
        #             "password": "12345678"
        #           }
        #         }'''
        data = '''{
            "command": "LOGIN", 
            "contents": {
                "email": "%s",
                "password": "%s"
              }
            }''' % (ID, PWD)
        try:
            json_data = json.loads(data)  # JSON 파싱
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('Invalid JSON format')

    def button2_clicked(self):
        global UUID
        global ID
        print('**** LOGOUT ****')
        # 버튼 2를 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
            "command": "LOGOUT",
            "contents": {
                "uuid": "%s",
                "email": "%s"
              }
            }''' % (UUID, ID)
        try:
            json_data = json.loads(data)  # JSON 파싱
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('Invalid JSON format')

    def button3_clicked(self):
        global UUID
        global ID
        print('**** INVITE ****')
        # 버튼 3을 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
                    "command": "INVITE",
                    "contents": {
                        "uuid": "%s",
                        "target": "%s"
                      }
                    }''' % (UUID, TARGET_ID)
        print(type(data))
        try:
            json_data = json.loads(data)  # JSON 파싱
            print(type(json_data))
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('button3 Invalid JSON format')

    def button4_clicked(self):
        global callid, UUID
        print('**** ACCEPT ****')
        # 버튼 4을 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
            "command": "ACCEPT",
            "contents": {
                "uuid": "%s",
                "callid": "%s"
              }
            }''' % (UUID, callid)
        print(type(data))
        try:
            json_data = json.loads(data)  # JSON 파싱
            print(type(json_data))
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('button3 Invalid JSON format')
        pass

    def button5_clicked(self):
        global callid, UUID
        print('**** CANCEL ****')
        # 버튼 4을 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
                    "command": "CANCEL",
                    "contents": {
                        "uuid": "%s",
                        "callid": "%s"
                      }
                    }''' % (UUID, callid)
        print(type(data))
        try:
            json_data = json.loads(data)  # JSON 파싱
            print(type(json_data))
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('button3 Invalid JSON format')
        pass

    def button6_clicked(self):
        global callid, UUID
        print('**** BYE ****')
        # 버튼 4을 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
            "command": "BYE",
            "contents": {
                "uuid": "%s",
                "callid": "%s"
              }
            }''' % (UUID, callid)
        print(type(data))
        try:
            json_data = json.loads(data)  # JSON 파싱
            print(type(json_data))
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('button3 Invalid JSON format')
        pass

    # def additional_button_clicked(self, num):
    #     print(f'Additional Button {num} clicked')
    #     # 추가 버튼을 클릭했을 때 실행할 코드를 여기에 추가


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())