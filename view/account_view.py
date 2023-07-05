from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class AccountView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Account View")

        self.button = QPushButton("Switch to Main View")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.label = QLabel("Account View")
        layout.addWidget(self.label)

        self.setLayout(layout)