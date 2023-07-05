import atexit
import socket
import json
import threading
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


HOST = '192.168.56.103'  # 서버의 IP 주소
PORT = 10000  # 서버의 포트 번호


# JSON 데이터를 서버로 전송하는 함수
def send_json_data(sock, data):
    json_data = json.dumps(data)  # JSON으로 직렬화
    sock.sendall(json_data.encode())


# JSON 데이터를 수신하는 함수
def receive_json_data(sock):
    json_data = sock.recv(1024).decode()
    data = json.loads(json_data)  # JSON 역직렬화
    return data


# 수신 쓰레드에서 실행될 함수
def receive_thread(sock):
    while True:
        try:
            received_data = receive_json_data(sock)
            print('Received data from server:', received_data)
        except json.JSONDecodeError:
            print('Invalid JSON format')
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
        self.resize(300, 600)

        # 버튼 생성 및 설정
        self.button1 = QPushButton('Login', self)
        self.button1.clicked.connect(self.button1_clicked)
        self.button1.setGeometry(50, 50, 100, 30)

        self.button2 = QPushButton('Logout', self)
        self.button2.clicked.connect(self.button2_clicked)
        self.button2.setGeometry(50, 100, 100, 30)

        # 추가 버튼 생성
        self.additional_buttons = []
        for i in range(3, 11):
            button = QPushButton(f'Button {i}', self)
            button.clicked.connect(lambda _, num=i: self.additional_button_clicked(num))
            button.setGeometry(50, 150 + (i-3) * 50, 100, 30)
            self.additional_buttons.append(button)

    def button1_clicked(self):
        print('Button 1 clicked')
        # 버튼 1을 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
        "command": "LOGIN", 
        "contents": {
            "email": "warebowl@gmail.com",
            "password": "12345678"
          }
        }'''
        try:
            json_data = json.loads(data)  # JSON 파싱
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('Invalid JSON format')

    def button2_clicked(self):
        print('Button 2 clicked')
        # 버튼 2를 클릭했을 때 실행할 코드를 여기에 추가
        data = '''{
                "command": "LOGOUT" 
                }'''
        try:
            json_data = json.loads(data)  # JSON 파싱
            send_json_data(sock, json_data)
        except json.JSONDecodeError:
            print('Invalid JSON format')

    def additional_button_clicked(self, num):
        print(f'Additional Button {num} clicked')
        # 추가 버튼을 클릭했을 때 실행할 코드를 여기에 추가


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

