﻿#include <gst/gst.h>

#define H264 1

#define LOOPBACK 1

int main(int argc, char* argv[])
{
    // Initialize GStreamer
    gst_init(&argc, &argv);

    // Create GStreamer pipline
    GstElement* pipeline = gst_pipeline_new("pipeline");

    // Create GStreamer pipline elements for video stream
    GstElement* videoSrc = gst_element_factory_make("mfvideosrc", "videoSrc");
    GstElement* videoCapsfilter = gst_element_factory_make("capsfilter", "videoCapsfilter");
#if H264
    GstElement* videoEnc = gst_element_factory_make("x264enc", "videoEnc");
    GstElement* videoPay = gst_element_factory_make("rtph264pay", "videoPay");
#endif // h264
    GstElement* videoSink = gst_element_factory_make("udpsink", "videoSink");
    
    // Create tee element
    GstElement* tee = gst_element_factory_make("tee", "tee");
    GstElement* queueDisplay = gst_element_factory_make("queue", "queueDisplay");
    GstElement* queueNetwork = gst_element_factory_make("queue", "queueNetwork");

    // Create video display elements
    GstElement* videoSinkDisplay = gst_element_factory_make("autovideosink", "videoSinkDisplay");

    // Create GStreamer pipline elements for audio
    GstElement* audioSrc = gst_element_factory_make("autoaudiosrc", "audioSrc");
    GstElement* audioConv = gst_element_factory_make("audioconvert", "audioConv");
    GstElement* audioResample = gst_element_factory_make("audioresample", "audioResample");
    GstElement* audioOpusenc = gst_element_factory_make("opusenc", "audioOpusenc");
    GstElement* audioPay = gst_element_factory_make("rtpopuspay", "audioPay");
    GstElement* audioSink = gst_element_factory_make("udpsink", "audioSink");

    // Add element to pipeline
    gst_bin_add_many(GST_BIN(pipeline), videoSrc, videoCapsfilter, videoEnc, videoPay, videoSink, tee, queueDisplay, queueNetwork, videoSinkDisplay, audioSrc, audioConv, audioResample, audioOpusenc, audioPay, audioSink, NULL);

    // linking elements for video
    gst_element_link_many(videoSrc, videoCapsfilter, tee, NULL);

    // Link video display elements
    GstPad* displayPad = gst_element_request_pad_simple(tee, "src_%u");
    GstPad* displaySinkPad = gst_element_get_static_pad(queueDisplay, "sink");
    gst_pad_link(displayPad, displaySinkPad);
    gst_element_link(queueDisplay, videoSinkDisplay);

    // Link video encoding elements
    GstPad* encodePad = gst_element_request_pad_simple(tee, "src_%u");
    GstPad* encodeSinkPad = gst_element_get_static_pad(queueNetwork, "sink");
    gst_pad_link(encodePad, encodeSinkPad);
    gst_element_link_many(queueNetwork, videoEnc, videoPay, videoSink, NULL);

    // Set video resolution
    GstCaps* videoCaps = gst_caps_from_string("video/x-raw, width=320, height=240");
    g_object_set(G_OBJECT(videoCapsfilter), "caps", videoCaps, NULL);
    gst_caps_unref(videoCaps);

    // linking elements for audio
    gst_element_link_many(audioSrc, audioConv, audioResample, audioOpusenc, audioPay, audioSink, NULL);

#if LOOPBACK
    // Set the receiving IP and port for video
    g_object_set(videoSink, "host", "127.0.0.1", "port", 5001, NULL);

    // Set the receiving IP and port for audio
    g_object_set(audioSink, "host", "127.0.0.1", "port", 5002, NULL);
#else
    // Set the receiving IP and port for video
    g_object_set(videoSink, "host", "192.168.2.4", "port", 5003, NULL);

    // Set the receiving IP and port for audio
    g_object_set(audioSink, "host", "192.168.2.4", "port", 5004, NULL);
#endif
    // set up laptop camera
    g_object_set(videoSrc, "device-index", 0, NULL);  // 0은 첫 번째 카메라를 나타냅니다.

#if H264
    // Set the tune attribute of the x264enc element to "zerolatency"
    g_object_set(videoEnc, "tune", 0x00000004, NULL);
#endif

    // generic (2049)               – Generic audio
    // voice (2048)                 – Voice
    // restricted-lowdelay (2051)   – Restricted low delay
    // Set the opusenc element's audio-type attribute to "restricted-lowdelay"
    g_object_set(audioOpusenc, "audio-type", 2051, NULL);

    // Pipeline execution
    GstStateChangeReturn ret = gst_element_set_state(pipeline, GST_STATE_PLAYING);
    if (ret == GST_STATE_CHANGE_FAILURE)
    {
        g_printerr("Unable to start the pipeline.\n");
        gst_object_unref(pipeline);
        return -1;
    }

    // Run main loop
    GstBus* bus = gst_element_get_bus(pipeline);
    GstMessage* msg;
    while ((msg = gst_bus_poll(bus, GST_MESSAGE_ANY, GST_CLOCK_TIME_NONE)))
    {
        GError* err;
        gchar* debug_info;
        switch (GST_MESSAGE_TYPE(msg))
        {
        case GST_MESSAGE_ERROR:
            gst_message_parse_error(msg, &err, &debug_info);
            g_printerr("Error received from element %s: %s\n", GST_OBJECT_NAME(msg->src), err->message);
            g_printerr("Debugging information: %s\n", debug_info ? debug_info : "none");
            g_error_free(err);
            g_free(debug_info);
            break;
        case GST_MESSAGE_EOS:
            g_print("End-Of-Stream reached.\n");
            break;
        case GST_MESSAGE_STATE_CHANGED:
        {
            GstState old_state, new_state, pending_state;
            gst_message_parse_state_changed(msg, &old_state, &new_state, &pending_state);
            g_print("State changed from %s to %s\n", gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));
            break;
        }
        case GST_MESSAGE_BUFFERING:
        {
            gint percent = 0;
            gst_message_parse_buffering(msg, &percent);
            g_print("Buffering %d%%\n", percent);
            break;
        }
        default:
            break;
        }
        gst_message_unref(msg);
    }

    // Release the pipeline
    gst_element_set_state(pipeline, GST_STATE_NULL);
    gst_object_unref(pipeline);
    return 0;
}