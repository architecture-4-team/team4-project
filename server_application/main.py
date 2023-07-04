import atexit

from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from services.network_manager import NetworkManager
from controller.network_controller import NetworkController

TCP_PORTS = [10000]
UDP_PORTS = [10001, 10002]


def cleanup():
    netMan.stop_network_services()

    # Perform other cleanup tasks
    print("Performing cleanup...")


atexit.register(cleanup)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()

    # initiate network
    netMan = NetworkManager(tcp_ports=TCP_PORTS, udp_ports=UDP_PORTS)
    # netMan.start_network_services()
    netCon = NetworkController(netMan)

    window.show()
    app.exec()
