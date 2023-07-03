#include "gstreamer_sender.h"
#include <gst/gst.h>
#include "global_setting.h"

static gboolean handle_sender_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data);
static GstPadProbeReturn probe_callback(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);

GMainLoop* senderLoop;
GstElement* senderVideoPipeline; 
GstElement* senderAudioPipeline;

int sender()
{
    // Create GStreamer pipline
    senderVideoPipeline = gst_pipeline_new("senderVideoPipeline");

    // Create GStreamer pipline elements for camera read
    GstElement* videoSrc = gst_element_factory_make("mfvideosrc", "videoSrc");
    GstElement* videoFlip = gst_element_factory_make("videoflip", "videoFlip"); // Create video flip element
    GstElement* videoCapsfilter = gst_element_factory_make("capsfilter", "videoCapsfilter");

    // Create tee element for multiple pad
    GstElement* tee = gst_element_factory_make("tee", "tee");

    // One for Network
    // Create Queue for parallel pipelining
    GstElement* queueNetwork = gst_element_factory_make("queue", "queueNetwork");
    // Create GStreamer pipline elements for video stream
    GstElement* videoEnc = gst_element_factory_make("x264enc", "videoEnc");
    GstElement* videoPay = gst_element_factory_make("rtph264pay", "videoPay");

    GstElement* videoSink = gst_element_factory_make("udpsink", "videoSink");

    // One for Display
    // Create Queue for parallel pipelining
    GstElement* queueDisplay = gst_element_factory_make("queue", "queueDisplay");
    // Create video display elements
    GstElement* videoSinkDisplay = gst_element_factory_make("autovideosink", "videoSinkDisplay");

    // Create GStreamer pipline elements for audio
    GstElement* audioSrc = gst_element_factory_make("autoaudiosrc", "audioSrc");
    GstElement* audioConv = gst_element_factory_make("audioconvert", "audioConv");
    GstElement* audioResample = gst_element_factory_make("audioresample", "audioResample");
    GstElement* audioOpusenc = gst_element_factory_make("opusenc", "audioOpusenc");
    GstElement* audioPay = gst_element_factory_make("rtpopuspay", "audioPay");

    GstElement* audioSink = gst_element_factory_make("udpsink", "audioSink");

    // Create GStreamer pipline
    senderAudioPipeline = gst_pipeline_new("senderAudioPipeline");

     // Add element to pipeline
    gst_bin_add_many(GST_BIN(senderVideoPipeline), videoSrc, videoFlip, videoCapsfilter,
        videoEnc, videoPay, videoSink, tee, queueDisplay, queueNetwork,
        videoSinkDisplay, NULL);

    gst_bin_add_many(GST_BIN(senderAudioPipeline), audioSrc, audioConv, audioResample, audioOpusenc,
        audioPay, audioSink, NULL);

    // linking elements for video
    gst_element_link_many(videoSrc, videoFlip, videoCapsfilter, tee, NULL);

    // Set video resolution
    GstCaps* videoCaps = gst_caps_from_string("video/x-raw, width=640, height=480");
    g_object_set(G_OBJECT(videoCapsfilter), "caps", videoCaps, NULL); // 해상도 조절
    gst_caps_unref(videoCaps);

    // 카메라 좌우반전
    g_object_set(G_OBJECT(videoFlip), "method", 4, NULL);  // 4 : 좌우반전

    // Link video display elements
    GstPad* displayPad = gst_element_request_pad_simple(tee, "src_%u");
    GstPad* displaySinkPad = gst_element_get_static_pad(queueDisplay, "sink");
    gst_pad_link(displayPad, displaySinkPad);
    gst_element_link(queueDisplay, videoSinkDisplay);

    // Link video network elements
    GstPad* networkPad = gst_element_request_pad_simple(tee, "src_%u");
    GstPad* networkSinkPad = gst_element_get_static_pad(queueNetwork, "sink");
    gst_pad_link(networkPad, networkSinkPad);
    gst_element_link_many(queueNetwork, videoEnc, videoPay, videoSink, NULL);

    // linking elements for audio
    gst_element_link_many(audioSrc, audioConv, audioResample, audioOpusenc, audioPay, audioSink, NULL);

    // Get the sink pad of the sink element
    GstPad* pad = gst_element_get_static_pad(videoSink, "sink");
    // Add a pad probe to the videoPay element
    gst_pad_add_probe(pad, GST_PAD_PROBE_TYPE_BUFFER, probe_callback, NULL, NULL);

    // Set payload number for rtph264pay
    g_object_set(G_OBJECT(videoPay), "payload", 96, NULL);

#if LOOPBACK
    // Set the receiving IP and port for video
    g_object_set(videoSink, "host", "127.0.0.1", "port", 5001, NULL);
    // Set the receiving IP and port for audio
    g_object_set(audioSink, "host", "127.0.0.1", "port", 5002, NULL);
#else
    // Set the receiving IP and port for video
    g_object_set(videoSink, "host", "192.168.1.128", "port", 5001, NULL);
    // Set the receiving IP and port for audio
    g_object_set(audioSink, "host", "192.168.1.128", "port", 5002, NULL);
#endif

    // set up laptop camera
    g_object_set(videoSrc, "device-index", 0, NULL);  // 0은 첫 번째 카메라를 나타냅니다.

    // Set the tune attribute of the x264enc element to "zerolatency"
    g_object_set(videoEnc, "tune", 0x00000004, NULL);

    // generic (2049)               – Generic audio
    // voice (2048)                 – Voice
    // restricted-lowdelay (2051)   – Restricted low delay
    // Set the opusenc element's audio-type attribute to "restricted-lowdelay"
    g_object_set(audioOpusenc, "audio-type", 2051, NULL);



    // Pipeline execution
    GstStateChangeReturn videoRet = gst_element_set_state(senderVideoPipeline, GST_STATE_PLAYING);
    GstStateChangeReturn audioRet = gst_element_set_state(senderAudioPipeline, GST_STATE_PLAYING);
    if (videoRet == GST_STATE_CHANGE_FAILURE || audioRet == GST_STATE_CHANGE_FAILURE)
    {
        g_printerr("Unable to start the pipeline.\n");
        gst_object_unref(senderVideoPipeline);
        gst_object_unref(senderAudioPipeline);
        return -1;
    }
    
    // Get the bus for the pipeline
    GstBus* bus = gst_element_get_bus(senderVideoPipeline);
    // Add a watch to the bus to receive messages
    gst_bus_add_watch(bus, (GstBusFunc)handle_sender_video_bus_message, NULL);
    gst_object_unref(bus);

    // Create a GMainLoop to handle events
    senderLoop = g_main_loop_new(NULL, FALSE);

    // Run the main loop
    g_main_loop_run(senderLoop);

    // Release the pipeline
    gst_element_set_state(senderVideoPipeline, GST_STATE_NULL);
    gst_element_set_state(senderAudioPipeline, GST_STATE_NULL);
    gst_object_unref(senderVideoPipeline);
    gst_object_unref(senderAudioPipeline);
    return 0;
}

// Function to handle bus messages
static gboolean handle_sender_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data)
{
    switch (GST_MESSAGE_TYPE(msg))
    {
    case GST_MESSAGE_ERROR:
    {
        GError* err;
        gchar* debug_info;
        gst_message_parse_error(msg, &err, &debug_info);
        g_printerr("Error received from element %s: %s\n", GST_OBJECT_NAME(msg->src), err->message);
        g_printerr("Debugging information: %s\n", debug_info ? debug_info : "none");
        g_error_free(err);
        g_free(debug_info);
        g_main_loop_quit(senderLoop); // Quit the main loop in case of an error
        break;
    }
    case GST_MESSAGE_EOS:
        g_print("End-Of-Stream reached.\n");
        g_main_loop_quit(senderLoop); // Quit the main loop when the end of the stream is reached
        break;
    case GST_MESSAGE_STATE_CHANGED:
    {
        GstState old_state, new_state, pending_state;
        gst_message_parse_state_changed(msg, &old_state, &new_state, &pending_state);
        g_print("Sender state changed from %s to %s\n", gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));
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

    return TRUE;
}

void stopSenderGstreamer(void) {
    g_main_loop_quit(senderLoop);
}

static GstPadProbeReturn probe_callback(GstPad* pad, GstPadProbeInfo* info, gpointer user_data) {
    GstBuffer* buffer = GST_PAD_PROBE_INFO_BUFFER(info);
    guint64 bufferSize = gst_buffer_get_size(buffer);
    guint64 timestamp = GST_BUFFER_TIMESTAMP(buffer);
    static guint64 prevTimestamp = 0;
    static guint64 totalBuffer = 0;

    // Calculate data rate in bits per second
    guint64 durationNs = timestamp - prevTimestamp;
    totalBuffer += bufferSize;
    if (durationNs > GST_SECOND)
    {
        guint64 dataRate = (totalBuffer * 8 * GST_SECOND) / durationNs;

        g_print("Send Data Rate: %lu bps\n", dataRate);

        totalBuffer = 0;
        prevTimestamp = timestamp;
    }

    return GST_PAD_PROBE_OK;
}