from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from view.main_view import MainView
from view.account_view import AccountView
from controller.main_controller import MainController
from controller.account_controller import AccountController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # MainWindow 설정
        self.setWindowTitle("Server Application")
        self.resize(800, 600)

        # StackedWidget 설정
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # MainView와 AccountView 인스턴스 생성
        self.main_view = MainView()
        self.account_view = AccountView()

        # StackedWidget에 뷰 추가
        self.stacked_widget.addWidget(self.main_view)
        self.stacked_widget.addWidget(self.account_view)

        # MainController 인스턴스 생성 및 View, Model 전달
        self.main_controller = MainController(self, self.main_view, self.account_view)
        self.account_controller = AccountController(self, self.main_view, self.account_view)

        # 버튼 클릭 이벤트 핸들러 연결
        self.main_view.button.clicked.connect(self.main_controller.main_button_clicked)
        self.account_view.button.clicked.connect(self.account_controller.account_button_clicked)
