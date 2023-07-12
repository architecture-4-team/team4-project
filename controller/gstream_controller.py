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

CLIENT_01_IP = '192.168.2.3'
CLIENT_02_IP = '192.168.2.2'
CLIENT_03_IP = '192.168.2.5'
CLIENT_04_IP = '192.168.2.7'


pipeline_map = {
    CLIENT_01_IP: {
        CLIENT_02_IP: (VIDEO_PORT_01, AUDIO_PORT_01),
        CLIENT_03_IP: (VIDEO_PORT_01, AUDIO_PORT_01),
        CLIENT_04_IP: (VIDEO_PORT_01, AUDIO_PORT_01)
    },
    CLIENT_02_IP: {
        CLIENT_01_IP: (VIDEO_PORT_01, AUDIO_PORT_01),
        CLIENT_03_IP: (VIDEO_PORT_02, AUDIO_PORT_02),
        CLIENT_04_IP: (VIDEO_PORT_02, AUDIO_PORT_02)
    },
    CLIENT_03_IP: {
        CLIENT_01_IP: (VIDEO_PORT_02, AUDIO_PORT_02),
        CLIENT_02_IP: (VIDEO_PORT_02, AUDIO_PORT_02),
        CLIENT_04_IP: (VIDEO_PORT_03, AUDIO_PORT_03)
    },
    CLIENT_04_IP: {
        CLIENT_01_IP: (VIDEO_PORT_03, AUDIO_PORT_03),
        CLIENT_02_IP: (VIDEO_PORT_03, AUDIO_PORT_03),
        CLIENT_03_IP: (VIDEO_PORT_03, AUDIO_PORT_03)
    },
}


class GStreamController(IEventReceiver):
    LOG = '[GStreamController]'

    connected_clients = list()
    pipelines: Dict[str, GStreamPipeline] = dict()
    pipeline_map: Dict[str, List[Tuple[str, int, int]]] = dict()
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
            sender_pipeline = self.pipelines.get(payload.room.sender_user.ip)
            receiver_pipeline = self.pipelines.get(payload.room.receiver_user.ip)
            if sender_pipeline and receiver_pipeline:
                # for sender
                self._add_signal(self.pipelines[payload.room.sender_user.ip], payload.room.receiver_user.ip,
                                 DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT)
                # for receiver
                self._add_signal(self.pipelines[payload.room.receiver_user.ip], payload.room.sender_user.ip,
                                 DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT)

                self._start_pipeline(payload.room.sender_user.ip)
                self._start_pipeline(payload.room.receiver_user.ip)

        if payload.state == CallState.BYE:
            print(self.LOG, 'Process bye state')
            sender_pipeline = self.pipelines.get(payload.room.sender_user.ip)
            receiver_pipeline = self.pipelines.get(payload.room.receiver_user.ip)
            if sender_pipeline and receiver_pipeline:
                # for sender
                self._remove_signal(self.pipelines[payload.room.sender_user.ip], payload.room.receiver_user.ip,
                                    DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT)
                # for receiver
                self._remove_signal(self.pipelines[payload.room.receiver_user.ip], payload.room.sender_user.ip,
                                    DEFAULT_SEND_VIDEO_PORT, DEFAULT_SEND_AUDIO_PORT)

            self._stop_pipeline(payload.room.sender_user.ip)
            self._stop_pipeline(payload.room.receiver_user.ip)

    def process_conf_state_changed(self, event: EventType, payload: RoomPayload):
        # only check user status
        if event == EventType.CONF_USER_JOINED:
            if payload.room:
                self._start_pipeline(payload.user.ip)

                participants = [user for user in payload.room.get_participated_members() if user.ip != payload.user.ip]
                for user in participants:
                    # participated members -> new user
                    conf_map = self.get_conference_map(user.ip)
                    self._add_signal(self.pipelines.get(user.ip), payload.user.ip,
                                     conf_map[payload.user.ip][0], conf_map[payload.user.ip][1])
                    print(self.LOG, 'Add Participant -> User', user.ip, payload.user.ip)
                    # New user -> participated members
                    conf_map = self.get_conference_map(payload.user.ip)
                    self._add_signal(self.pipelines.get(payload.user.ip), user.ip,
                                     conf_map[user.ip][0], conf_map[user.ip][1])
                    print(self.LOG, 'Add User -> Participant', payload.user.ip, user.ip)

        if event == EventType.CONF_USER_LEAVED:
            if payload.room:
                self._stop_pipeline(payload.user.ip)

                # participated members add new user
                participants = [user for user in payload.room.get_participated_members() if user.ip != payload.user.ip]
                for user in participants:
                    # participated members add new user
                    conf_map = self.get_conference_map(user.ip)
                    self._remove_signal(self.pipelines.get(user.ip), payload.user.ip,
                                        conf_map[payload.user.ip][0], conf_map[payload.user.ip][1])
                    print(self.LOG, 'Remove Participant -> User', user.ip, payload.user.ip)
                    # New user add participated members
                    conf_map = self.get_conference_map(payload.user.ip)
                    self._remove_signal(self.pipelines.get(payload.user.ip), user.ip,
                                        conf_map[user.ip][0], conf_map[user.ip][1])
                    print(self.LOG, 'Remove User -> Participant', payload.user.ip, user.ip)

        if event == EventType.CONF_STATE_CHANGED:
            pass

    def send_data(self, data, sender, rcv_port):
        if pipeline := self.pipelines.get(sender):
            if rcv_port == DEFAULT_RCV_VIDEO_PORT:
                pipeline.relay_video(data)
            elif rcv_port == DEFAULT_RCV_AUDIO_PORT:
                pipeline.relay_audio(data)

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

    def _add_signal(self, pipeline: GStreamPipeline, dst_ip, dst_vport, dst_aport):
        if pipeline:
            pipeline.vsink.emit('add', dst_ip, dst_vport)
            pipeline.asink.emit('add', dst_ip, dst_aport)
        else:
            print(self.LOG, 'add no pipeline')

    def _remove_signal(self, pipeline: GStreamPipeline, dst_ip, dst_vport, dst_aport):
        if pipeline:
            pipeline.vsink.emit('remove', dst_ip, dst_vport)
            pipeline.asink.emit('remove', dst_ip, dst_aport)
        else:
            print(self.LOG, 'remove no pipeline')

    def get_pipeline_map(self, host):
        return self.pipeline_map.get(host)

    def get_conference_map(self, host):
        return pipeline_map[host]
