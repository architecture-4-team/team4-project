class MainController:
    def __init__(self, main_window, main_view, account_view):
        self.main_window = main_window
        self.main_view = main_view
        self.account_view = account_view

    def main_button_clicked(self):
        self.main_window.stacked_widget.setCurrentWidget(self.account_view)
