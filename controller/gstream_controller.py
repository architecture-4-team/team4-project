import threading
from typing import Dict, List, Tuple

from controller.gstream_pipeline import GStreamPipeline
from model.callbroker import callbroker_service
from model.conferencecall_broker import conferencecallbroker
from model.directory_singleton import directory_service
from model.user import UserExt
from services.ievent_receiver import IEventReceiver, EventType, UserPayload, EventPayload, TCPPayload, UDPPayload, \
    RoomPayload
from services.network_manager import NetworkManager, ProtocolType
from utils.call_state import CallState

DEFAULT_RCV_VIDEO_PORT = 10001
DEFAULT_RCV_AUDIO_PORT = 10002

DEFAULT_SEND_VIDEO_PORT = 5001
DEFAULT_SEND_AUDIO_PORT = 5002

VIDEO_PORT_01 = 5001
AUDIO_PORT_01 = 5002
VIDEO_PORT_02 = 5003
AUDIO_PORT_02 = 5004
VIDEO_PORT_03 = 5005
AUDIO_PORT_03 = 5006

CLIENT_01_IP = '192.168.2.4'
CLIENT_02_IP = '192.168.2.5'
CLIENT_03_IP = '192.168.2.6'
CLIENT_04_IP = '192.168.2.7'


pipeline_map = {
    CLIENT_01_IP: [
        (CLIENT_02_IP, VIDEO_PORT_01, AUDIO_PORT_01),
        (CLIENT_03_IP, VIDEO_PORT_01, AUDIO_PORT_01),
        (CLIENT_04_IP, VIDEO_PORT_01, AUDIO_PORT_01)
    ],
    CLIENT_02_IP: [
        (CLIENT_01_IP, VIDEO_PORT_01, AUDIO_PORT_01),
        (CLIENT_03_IP, VIDEO_PORT_02, AUDIO_PORT_02),
        (CLIENT_04_IP, VIDEO_PORT_02, AUDIO_PORT_02)
    ],
    CLIENT_03_IP: [
        (CLIENT_01_IP, VIDEO_PORT_02, AUDIO_PORT_02),
        (CLIENT_02_IP, VIDEO_PORT_02, AUDIO_PORT_02),
        (CLIENT_04_IP, VIDEO_PORT_03, AUDIO_PORT_03)
    ],
    CLIENT_04_IP: [
        (CLIENT_01_IP, VIDEO_PORT_03, AUDIO_PORT_03),
        (CLIENT_02_IP, VIDEO_PORT_03, AUDIO_PORT_03),
        (CLIENT_03_IP, VIDEO_PORT_03, AUDIO_PORT_03)
    ],
}


class GStreamController(IEventReceiver):
    LOG = '[GStreamController]'

    connected_clients = list()
    pipelines: Dict[str, GStreamPipeline] = dict()
    pipeline_map: Dict[str, List[Tuple[UserExt, int, int]]] = dict()
    one2one_participants = list()
    route_map = None

    def __init__(self):
        self.route_map = {
            EventType.USER_ADDED: self.process_user,
            EventType.USER_REMOVED: self.process_user,
            EventType.CLIENT_CONNECTED: self.process_connection,
            EventType.CLIENT_DISCONNECTED: self.process_connection,
            EventType.UDP_DATA_RECEIVED: self.process_udp,
            EventType.STATE_CHANGED: self.process_state_changed,
            EventType.CONF_STATE_CHANGED: self.process_conf_state_changed,
            EventType.CONF_USER_JOINED: self.process_conf_state_changed,
            EventType.CONF_USER_LEAVED: self.process_conf_state_changed
        }

    def start(self):
        NetworkManager.subscribe(self, ProtocolType.UDP, DEFAULT_RCV_VIDEO_PORT)
        NetworkManager.subscribe(self, ProtocolType.UDP, DEFAULT_RCV_AUDIO_PORT)

        directory_service.subscribe(self)
        callbroker_service.subscribe(self)
        conferencecallbroker.subscribe(self)

    def receive(self, event_name: EventType, event: EventPayload):
        # print(self.LOG, 'Receive event: ', event_name)
        self.route_map[event_name](event_name, event)

    def process_connection(self, event_name: EventType, payload: TCPPayload):
        host, port = payload.socket.getpeername()
        if event_name == EventType.CLIENT_CONNECTED:
            pass
        if event_name == EventType.CLIENT_DISCONNECTED:
            self.pipelines.pop(host)
        print(self.LOG, 'Client connection: ', host, port, event_name)

    def process_udp(self, event_name: EventType, payload: UDPPayload):
        if event_name == EventType.UDP_DATA_RECEIVED:
            self.send_data(payload.packet, payload.sender_ip, payload.receive_port)

    def process_user(self, event, payload: UserPayload):
        if event == "user-added":
            print(self.LOG, 'user added: ', payload.user.email)
            receive_thread = threading.Thread(target=self._create_user_pipelie,
                                              args=(payload.user,), daemon=True)
            receive_thread.start()
        if event == 'user-removed':
            print(self.LOG, 'user removed: ', payload.user.email)
            self._stop_pipeline(payload.user.ip)

    def process_state_changed(self, event, payload: RoomPayload):
        if payload.state == CallState.CALLING:
            print(self.LOG, 'Process calling state')
            if not self.pipeline_map.get(payload.room.sender_user.ip):
                self.pipeline_map[payload.room.sender_user.ip] = list()
            self.pipeline_map[payload.room.sender_user.ip].\
                append((payload.room.receiver_user, DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT))
            if not self.pipeline_map.get(payload.room.receiver_user.ip):
                self.pipeline_map[payload.room.receiver_user.ip] = list()
            self.pipeline_map[payload.room.receiver_user.ip].\
                append((payload.room.sender_user, DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT))

            self._start_pipeline(payload.room.sender_user.ip)
            self._start_pipeline(payload.room.receiver_user.ip)

            self.one2one_participants.append(payload.room.sender_user.ip)
            self.one2one_participants.append(payload.room.receiver_user.ip)

        if payload.state == CallState.BYE:
            print(self.LOG, 'Process bye state')
            self.pipeline_map.pop(payload.room.sender_user.ip)
            self.pipeline_map.pop(payload.room.receiver_user.ip)

            self._stop_pipeline(payload.room.sender_user.ip)
            self._stop_pipeline(payload.room.receiver_user.ip)

            self.one2one_participants.remove(payload.room.sender_user.ip)
            self.one2one_participants.remove(payload.room.receiver_user.ip)

    def process_conf_state_changed(self, event: EventType, payload: RoomPayload):
        # only check user status
        if event == EventType.CONF_USER_JOINED:
            self._start_pipeline(payload.user.ip)
        if event == EventType.CONF_USER_LEAVED:
            self._stop_pipeline(payload.user.ip)

        if event == EventType.CONF_STATE_CHANGED:
            pass

    def send_data(self, data, sender, rcv_port):
        if self.one2one_participants:
            target_map = self.get_pipeline_map(sender)
        else:
            target_map = self.get_conference_map(sender)
        if pipeline := self.pipelines.get(sender):
            for target in target_map:
                if rcv_port == DEFAULT_RCV_VIDEO_PORT:
                    pipeline.relay_video(data, target[0].ip, target[1], sender)
                elif rcv_port == DEFAULT_RCV_AUDIO_PORT:
                    pipeline.relay_audio(data, target[0].ip, target[2], sender)

    def _start_pipeline(self, target):
        print(self.LOG, 'Start pipeline: ', target)

    def _stop_pipeline(self, target):
        self.pipelines[target].stop()
        print(self.LOG, 'Stop pipeline: ', target)

    def _create_user_pipelie(self, user: UserExt):
        pipeline = GStreamPipeline(user.ip)
        self.pipelines[user.ip] = pipeline
        pipeline.start()

    def _remove_user_pipeline(self, user: UserExt):
        self._stop_pipeline(user.ip)
        self.pipelines.pop(user.ip)

    def get_pipeline_map(self, host):
        return self.pipeline_map[host]

    def get_conference_map(self, host):
        return pipeline_map[host]
