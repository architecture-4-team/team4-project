import socket

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)


def receive_stream(rcv_port):
    pipeline = Gst.Pipeline()
    udpsrc = Gst.ElementFactory.make("udpsrc", "udpsrc")
    capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
    rtph264depay = Gst.ElementFactory.make("rtph264depay", "rtph264depay")
    h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
    avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
    autovideosink = Gst.ElementFactory.make("autovideosink", "autovideosink")

    # add elements
    pipeline.add(udpsrc)
    pipeline.add(capsfilter)
    pipeline.add(rtph264depay)
    pipeline.add(h264parse)
    pipeline.add(avdec_h264)
    pipeline.add(autovideosink)

    # set property
    udpsrc.set_property("port", rcv_port)
    capsfilter.set_property("caps", Gst.caps_from_string(
        "application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264"))

    udpsrc.link(capsfilter)
    capsfilter.link(rtph264depay)
    rtph264depay.link(h264parse)
    h264parse.link(avdec_h264)
    avdec_h264.link(autovideosink)

    pipeline.set_state(Gst.State.PLAYING)
    print("Receiver started")

    try:
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        pass

    pipeline.set_state(Gst.State.NULL)
    print("Receiver stopped")


if __name__ == '__main__':
    receive_stream(5001)
