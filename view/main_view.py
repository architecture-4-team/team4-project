from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        # 버튼 생성
        self.button = QPushButton("Switch to Account View")
        self.conference = QPushButton("Make the conference call")
        self.del_conference = QPushButton("Delete the conference call")

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.conference)
        layout.addWidget(self.del_conference)
        self.label = QLabel("Main View")
        layout.addWidget(self.label)
        self.setLayout(layout)
        