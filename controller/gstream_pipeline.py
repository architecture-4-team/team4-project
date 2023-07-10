# user : pipeline = 1 : 1
from datetime import datetime

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)


class GStreamPipeline:
    PIPELINE_STR = 'appsrc name=src ! multiudpsink name=sink'

    owner: str = ''     # sender ip
    vpipeline = None
    vsrc = None
    vsink = None

    apipeline = None
    asrc = None
    asink = None

    clients = list()

    def __init__(self, owner):
        self.owner = owner
        self.vpipeline = Gst.parse_launch(self.PIPELINE_STR)
        self.vsrc = self.vpipeline.get_by_name("src")
        self.vsink = self.vpipeline.get_by_name("sink")

        self.apipeline = Gst.parse_launch(self.PIPELINE_STR)
        self.asrc = self.apipeline.get_by_name("src")
        self.asink = self.apipeline.get_by_name("sink")

    def start(self):
        self.vpipeline.set_state(Gst.State.PLAYING)
        self.apipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.vpipeline.set_state(Gst.State.NULL)
        self.vpipeline = None
        self.apipeline.set_state(Gst.State.NULL)
        self.apipeline = None

    def relay_video(self, data, dst_ip, dst_port, sender=None):
        print(f'[{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}][V]', dst_ip, dst_port)
        if f"{dst_ip}:{dst_port}" not in self.clients:
            self.vsink.emit("add", dst_ip, dst_port)
            self.clients.append(f"{dst_ip}:{dst_port}")
        # header = f'{len(sender)}{sender}'
        data = sender.encode() + data
        buffer = Gst.Buffer.new_wrapped(data)
        self.vsrc.emit("push-buffer", buffer)

    def relay_audio(self, data, dst_ip, dst_port, sender=None):
        print(f'[{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}][A]', dst_ip, dst_port)
        if f"{dst_ip}:{dst_port}" not in self.clients:
            self.asink.emit("add", dst_ip, dst_port)
            self.clients.append(f"{dst_ip}:{dst_port}")
        buffer = Gst.Buffer.new_wrapped(data)
        self.asrc.emit("push-buffer", buffer)
