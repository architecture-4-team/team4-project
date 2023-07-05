import datetime
import socket
import threading
from services.network.inetwork_service import INetworkService

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)


# for testing
# service = UDPGStreamerService(10001)
# service.set_target("127.0.0.1", 5001)
# service.start()
#
# while True:
#     input_data = input('Enter JSON data to send (or "quit" to exit): ')
#     if input_data == 'quit':
#         service.stop()
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
        self.socket.bind(('localhost', self.port))

    def start(self):
        print('start')
        th = threading.Thread(target=self.relay)
        th.start()

    def stop(self):
        if self.g_loop:
            self.g_loop.quit()
            print('g_loop quit')
        self.pipeline.set_state(Gst.State.NULL)
        print('set state')
        self.socket.close()
        print('socket close')

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

        # Create the pipeline
        # pipeline_str = 'appsrc name=src ! queue ! multiudpsink name=sink'
        # pipeline = Gst.parse_launch(pipeline_str)
        if not self.pipeline:
            self.pipeline = Gst.Pipeline()

            # Create elements
            src = Gst.ElementFactory.make('appsrc', 'src')
            # queue = Gst.ElementFactory.make('queue', 'queue')
            sink = Gst.ElementFactory.make('multiudpsink', 'sink')

            # Add elements to the pipeline
            self.pipeline.add(src)
            # self.pipeline.add(queue)
            self.pipeline.add(sink)

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
        # sender_ip = addr[0]
        # sender_port = addr[1]
        # print('[', datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), ']', sender_ip, sender_port)
        if f"{self.dst_ip}:{self.dst_port}" not in self.clients:
            sink.emit("add", self.dst_ip, self.dst_port)
            self.clients.append(f"{self.dst_ip}:{self.dst_port}")

        # https://lifestyletransfer.com/how-to-make-gstreamer-buffer-writable-in-python/
        buffer = Gst.Buffer.new_wrapped(data)
        src.emit("push-buffer", buffer)
