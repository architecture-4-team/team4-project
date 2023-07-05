import datetime
import socket
import threading
from services.network.inetwork_service import INetworkService

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)


# for testing
# video_rcv_port = 10001
# audio_rcv_port = 10002
#
# # dst_ip = "127.0.0.1"
# # dst_ip = "192.168.29.231"
# dst_ip = "192.168.2.4"
# dst_vport = 5001
# dst_aport = 5002
#
# video_service = UDPGStreamerService(video_rcv_port)
# video_service.set_target(dst_ip, dst_vport)
# video_service.start()
#
# audio_service = UDPGStreamerService(audio_rcv_port)
# audio_service.set_target(dst_ip, dst_aport)
# audio_service.start()
#
# while True:
#     input_data = input('Enter JSON data to send (or "quit" to exit): ')
#     if input_data == 'quit':
#         video_service.stop()
#         audio_service.stop()
#         break


class UDPGStreamerService(INetworkService):
    buf_size: int = 50 * 1024
    port: int
    socket = None
    dst_ip: str
    dst_port: int = -1
    pipeline = None
    g_loop = None
    clients = list()

    def __init__(self, port: int):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))

    def start(self):
        print('start')
        th = threading.Thread(target=self.relay)
        th.start()

    def stop(self):
        if self.g_loop:
            self.g_loop.quit()
            print('g_loop quit')
        self.socket.close()
        print('socket close')
        self.pipeline.set_state(Gst.State.NULL)
        print('set state')

    def send(self, data):
        pass

    def receive(self):
        pass

    def set_buf_size(self, buf_size):
        self.buf_size = buf_size

    def set_target(self, dst_ip, dst_port):
        self.dst_ip = dst_ip
        self.dst_port = dst_port

    def relay(self):
        if not self.dst_ip or self.dst_port == -1:
            print("Decide destination ip or port")
            return

        # print('start relay')
        # Create the pipeline
        # pipeline_str = 'appsrc name=src ! queue ! multiudpsink name=sink'
        # self.pipeline = Gst.parse_launch(pipeline_str)
        # src = self.pipeline.get_by_name("src")
        # sink = self.pipeline.get_by_name("sink")
        # src.connect('need-data', self.cb_need_data, sink)
        if not self.pipeline:
            self.pipeline = Gst.Pipeline()

            # Create elements
            src = Gst.ElementFactory.make('appsrc', 'src')
            # queue = Gst.ElementFactory.make('queue', 'queue')
            sink = Gst.ElementFactory.make('multiudpsink', 'sink')
            # src = Gst.ElementFactory.make('udpsrc', 'src')
            # sink = Gst.ElementFactory.make('udpsink', 'sink')

            # Add elements to the pipeline
            self.pipeline.add(src)
            # self.pipeline.add(queue)
            self.pipeline.add(sink)

            # sink.set_property("host", self.dst_ip)
            # sink.set_property("port", self.dst_port)

            # Link elements
            # src.link(queue)
            # queue.link(sink)
            src.link(sink)

            src.connect('need-data', self.cb_need_data, sink)

        self.pipeline.set_state(Gst.State.PLAYING)
        self.g_loop = GLib.MainLoop()
        self.g_loop.run()
        print('end relay')

    def cb_need_data(self, src, length, sink):
        data, addr = self.socket.recvfrom(self.buf_size)
        sender_ip = addr[0]
        sender_port = addr[1]
        print(f'[{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}]', sender_ip, sender_port)
        if f"{self.dst_ip}:{self.dst_port}" not in self.clients:
            sink.emit("add", self.dst_ip, self.dst_port)
            self.clients.append(f"{self.dst_ip}:{self.dst_port}")

        # https://lifestyletransfer.com/how-to-make-gstreamer-buffer-writable-in-python/
        buffer = Gst.Buffer.new_wrapped(data)
        src.emit("push-buffer", buffer)
