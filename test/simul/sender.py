import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)


def start_stream(dst_port):
    pipeline = Gst.Pipeline()
    avfvideosrc = Gst.ElementFactory.make("avfvideosrc", "avfvideosrc")
    videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
    x264enc = Gst.ElementFactory.make("x264enc", "x264enc")
    h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
    rtph264pay = Gst.ElementFactory.make("rtph264pay", "rtph264pay")
    udpsink = Gst.ElementFactory.make("udpsink", "udpsink")

    pipeline.add(avfvideosrc)
    pipeline.add(videoconvert)
    pipeline.add(x264enc)
    pipeline.add(h264parse)
    pipeline.add(rtph264pay)
    pipeline.add(udpsink)

    avfvideosrc.set_property("device-index", 0)  # Specify the device index if multiple cameras are available

    udpsink.set_property("host", "127.0.0.1")
    udpsink.set_property("port", dst_port)

    avfvideosrc.link(videoconvert)
    videoconvert.link(x264enc)
    x264enc.link(h264parse)
    h264parse.link(rtph264pay)
    rtph264pay.link(udpsink)

    pipeline.set_state(Gst.State.PLAYING)
    print("Sender started")

    try:
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        pass

    pipeline.set_state(Gst.State.NULL)
    print("Sender stopped")


if __name__ == '__main__':
    start_stream(10001)
