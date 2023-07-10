from typing import Dict

from controller.gstream_pipeline import GStreamPipeline
from services.network_manager import INetworkEventReceiver, NetworkManager, EventType


pipeline_map = {
    "192.168.2.4": [
        ("192.168.2.4", 5001, 5002)
    ],
    "192.168.2.8": [
        ("192.168.2.8", 5001, 5002)
    ]
}


class GStreamController(INetworkEventReceiver):

    connected_clients = list()
    pipelines: Dict[str, GStreamPipeline] = dict()

    def __init__(self):
        pass

    def start(self):
        NetworkManager.subscribe_tcp(10000, EventType.CLIENT_CONNECTED, self)
        NetworkManager.subscribe_tcp(10000, EventType.CLIENT_DISCONNECTED, self)

        NetworkManager.subscribe_udp(10001, EventType.DATA_RECEIVED, self)
        NetworkManager.subscribe_udp(10002, EventType.DATA_RECEIVED, self)

        pipeline = GStreamPipeline("192.168.2.8")
        self.pipelines["192.168.2.8"] = pipeline
        pipeline.start()

        pipeline = GStreamPipeline("192.168.2.4")
        self.pipelines["192.168.2.4"] = pipeline
        pipeline.start()

    def receive_tcp(self, socket, event=None):
        host, port = socket.getpeername()
        self.manage_connection(host, event)

    def receive_udp(self, data, sender_ip, rcv_port):
        self.send_data(data, sender_ip, rcv_port)

    def manage_connection(self, sender, event):
        if event == EventType.CLIENT_CONNECTED and sender not in self.connected_clients:
            self.connected_clients.append(sender)
            self.pipelines[sender] = GStreamPipeline(sender)
        if event == EventType.CLIENT_DISCONNECTED and sender in self.connected_clients:
            self.connected_clients.remove(sender)
            if pipeline := self.pipelines.get(sender):
                pipeline.stop()
                self.pipelines.pop(sender)

    def send_data(self, data, sender, rcv_port):
        target_map = self.get_pipeline_map(sender)
        if pipeline := self.pipelines.get(sender):
            for target in target_map:
                if rcv_port == 10001:
                    pipeline.relay_video(data, target[0], target[1], sender)
                elif rcv_port == 10002:
                    pipeline.relay_audio(data, target[0], target[2], sender)

    def get_pipeline_map(self, host):
        return pipeline_map[host]
