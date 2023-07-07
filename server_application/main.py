import atexit

from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from services.network_manager import NetworkManager
from controller.network_controller import NetworkController
#from services.storage_manager import StorageManager
#from services.storage.istorage_service import IStorageService
#from services.storage.mysql_service import MySQLService
#from model.login import Login

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

    # 초기화 작업

    # initiate network
    netMan = NetworkManager(tcp_ports=TCP_PORTS, udp_ports=UDP_PORTS)
    # netMan.start_network_services()
    netCon = NetworkController(netMan)

    # ifStorage: IStorageService = MySQLService()
    # storageMan = StorageManager(ifStorage)
    # storageMan.connect_to_database()

    # login = Login()

    # signal/slot mapping information
    # netCon.signal_login.connect(login.receive_message)

    window.show()
    app.exec()
