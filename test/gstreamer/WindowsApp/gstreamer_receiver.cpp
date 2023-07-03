#include "gstreamer_receiver.h"
#include <gst/gst.h>
#include "global_setting.h"

static gboolean handle_receiver_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data);
static GstPadProbeReturn probe_callback(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);

GMainLoop* receiverLoop;
GstElement* videoPipeline;
GstElement* audioPipeline;

int receiver()
{
    // Create GStreamer pipline for video
    videoPipeline = gst_pipeline_new("videoReceiver_pipeline");

    // Create GStreamer pipline elements for video
    GstElement* videoSrc = gst_element_factory_make("udpsrc", "videoSrc");
    GstElement* videoCapsfilter = gst_element_factory_make("capsfilter", "videoCapsfilter");
    GstElement* jitterbufferVideo = gst_element_factory_make("rtpjitterbuffer", "jitterbufferVideo");
    GstElement* videoDepay = gst_element_factory_make("rtph264depay", "videoDepay");
    GstElement* videoDec = gst_element_factory_make("avdec_h264", "videoDec");
    GstElement* videoSink = gst_element_factory_make("autovideosink", "videoSink");

    // Create GStreamer pipline for audio
    audioPipeline = gst_pipeline_new("audioReceiver_pipeline");

    // Create GStreamer pipline elements for audio
    GstElement* audioSrc = gst_element_factory_make("udpsrc", "audioSrc");
    GstElement* audioCapsfilter = gst_element_factory_make("capsfilter", "audioCapsfilter");
    GstElement* jitterbufferAudio = gst_element_factory_make("rtpjitterbuffer", "jitterbufferAudio");
    GstElement* audioDec = gst_element_factory_make("opusdec", "audioDec");
    GstElement* audioDepay = gst_element_factory_make("rtpopusdepay", "audioDepay");
    GstElement* audioConv = gst_element_factory_make("audioconvert", "audioConv");
    GstElement* audioSink = gst_element_factory_make("autoaudiosink", "audioSink");

    // Add element to pipeline
    gst_bin_add_many(GST_BIN(videoPipeline), videoSrc, videoCapsfilter, jitterbufferVideo, videoDepay, videoDec, videoSink, NULL);
    gst_bin_add_many(GST_BIN(audioPipeline), audioSrc, audioCapsfilter, jitterbufferAudio, audioDec, audioDepay, audioConv, audioSink, NULL);
    
    // linking elements
    gst_element_link_many(videoSrc, videoCapsfilter, jitterbufferVideo, videoDepay, videoDec, videoSink, NULL);
    gst_element_link_many(audioSrc, audioCapsfilter, jitterbufferAudio, audioDepay, audioDec, audioConv, audioSink, NULL);

    // Get the sink pad of the sink element
    GstPad* pad = gst_element_get_static_pad(videoCapsfilter, "sink");
    gst_pad_add_probe(pad, GST_PAD_PROBE_TYPE_BUFFER, probe_callback, NULL, NULL);

#if LOOPBACK
    // Receive port setting
    g_object_set(videoSrc, "port", 5001, NULL);
    g_object_set(audioSrc, "port", 5002, NULL);
#else
    // Receive port setting
    g_object_set(videoSrc, "port", 5003, NULL);
    g_object_set(audioSrc, "port", 5004, NULL);
#endif

    // latency: 지터 버퍼의 대기 시간(밀리초)을 설정합니다. 이 값은 네트워크 지연을 허용하는 최대 시간을 나타냅니다. 기본값은 200ms입니다.
    // drop - on - latency: 이 속성이 true로 설정되면, 지터 버퍼는 대기 시간 초과 패킷을 버립니다.기본값은 false입니다.
    g_object_set(G_OBJECT(jitterbufferVideo), "latency", 200, "do-lost", TRUE, NULL);
    g_object_set(G_OBJECT(jitterbufferAudio), "latency", 200, "do-lost", TRUE, NULL);

    // RTP video format (caps) settings
    GstCaps* videoCaps = gst_caps_from_string("application/x-rtp, media=(string)video, payload=(int)96");
    g_object_set(G_OBJECT(videoCapsfilter), "caps", videoCaps, NULL);
    gst_caps_unref(videoCaps);

    // RTP audio format (caps) settings
    GstCaps* audioCaps = gst_caps_from_string("application/x-rtp, media=(string)audio, encoding-name=OPUS,  payload=(int)96");
    g_object_set(G_OBJECT(audioCapsfilter), "caps", audioCaps, NULL);
    gst_caps_unref(audioCaps);

    // Pipeline execution
    GstStateChangeReturn videoRet = gst_element_set_state(videoPipeline, GST_STATE_PLAYING);
    GstStateChangeReturn audioRet = gst_element_set_state(audioPipeline, GST_STATE_PLAYING);
    if (videoRet == GST_STATE_CHANGE_FAILURE || audioRet == GST_STATE_CHANGE_FAILURE)
    {
        g_printerr("Unable to start the pipeline.\n");
        gst_object_unref(videoPipeline);
        gst_object_unref(audioPipeline);
        return -1;
    }

    // Get the bus for the pipeline
    GstBus* bus = gst_element_get_bus(videoPipeline);

    // Add a watch to the bus to receive messages
    gst_bus_add_watch(bus, (GstBusFunc)handle_receiver_video_bus_message, NULL);
    gst_object_unref(bus);

    // Create a GMainLoop to handle events
    receiverLoop = g_main_loop_new(NULL, FALSE);

    // Run the main loop
    g_main_loop_run(receiverLoop);

    // Release the pipeline
    gst_element_set_state(videoPipeline, GST_STATE_NULL);
    gst_element_set_state(audioPipeline, GST_STATE_NULL);

    // Remove the elements from the pipeline
    gst_bin_remove_many(GST_BIN(videoPipeline), videoSrc, videoCapsfilter, videoDepay, videoDec, videoSink, NULL);
    gst_bin_remove_many(GST_BIN(audioPipeline), audioSrc, audioCapsfilter, audioDec, audioDepay, audioConv, audioSink, NULL);

    // Unref the elements
    gst_object_unref(videoSrc);
    gst_object_unref(videoCapsfilter);
    gst_object_unref(videoDepay);
    gst_object_unref(videoDec);
    gst_object_unref(videoSink);

    gst_object_unref(audioSrc);
    gst_object_unref(audioCapsfilter);
    gst_object_unref(audioDec);
    gst_object_unref(audioDepay);
    gst_object_unref(audioConv);
    gst_object_unref(audioSink);

    gst_object_unref(videoPipeline);
    gst_object_unref(audioPipeline);
    return 0;
}

// Function to handle bus messages
static gboolean handle_receiver_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data)
{
    switch (GST_MESSAGE_TYPE(msg))
    {
    case GST_MESSAGE_ERROR:
        GError* err;
        gchar* debug_info;
        gst_message_parse_error(msg, &err, &debug_info);
        g_printerr("Error received from element %s: %s\n", GST_OBJECT_NAME(msg->src), err->message);
        g_printerr("Debugging information: %s\n", debug_info ? debug_info : "none");
        g_error_free(err);
        g_free(debug_info);
        g_main_loop_quit(receiverLoop); // Quit the main loop in case of an error
        break;
    case GST_MESSAGE_EOS:
        g_print("End-Of-Stream reached.\n");
        g_main_loop_quit(receiverLoop); // Quit the main loop when the end of the stream is reached
        break;
    case GST_MESSAGE_STATE_CHANGED:
    {
        GstState old_state, new_state, pending_state;
        gst_message_parse_state_changed(msg, &old_state, &new_state, &pending_state);
        g_print("Receiver state changed from %s to %s\n", gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));
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

    return TRUE;
}

void stopReceiverGstreamer(void) {
    g_main_loop_quit(receiverLoop);
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

        g_print("Receive Data Rate: %lu bps\n", dataRate);

        totalBuffer = 0;
        prevTimestamp = timestamp;
    }

    return GST_PAD_PROBE_OK;
}