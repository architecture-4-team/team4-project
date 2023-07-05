from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        # 버튼 생성
        self.button = QPushButton("Switch to Account View")

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.label = QLabel("Main View")
        layout.addWidget(self.label)
        self.setLayout(layout)