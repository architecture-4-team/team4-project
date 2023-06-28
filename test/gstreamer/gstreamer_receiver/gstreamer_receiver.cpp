#include <gst/gst.h>

int main(int argc, char* argv[])
{
    // Initialize GStreamer
    gst_init(&argc, &argv);

    // Create GStreamer pipline for video
    GstElement* videoPipeline = gst_pipeline_new("videoReceiver_pipeline");

    // Create GStreamer pipline elements for video
    GstElement* videoSrc = gst_element_factory_make("udpsrc", "videoSrc");
    GstElement* videoCapsfilter = gst_element_factory_make("capsfilter", "videoCapsfilter");
    //x.264
    GstElement* videoDepay = gst_element_factory_make("rtph264depay", "videoDepay");
    GstElement* videoDec = gst_element_factory_make("avdec_h264", "videoDec");
    GstElement* videoSink = gst_element_factory_make("autovideosink", "videoSink");

    // Create GStreamer pipline for audio
    GstElement* audioPipeline = gst_pipeline_new("audioReceiver_pipeline");

    // Create GStreamer pipline elements for audio
    GstElement* audioSrc = gst_element_factory_make("udpsrc", "audioSrc");
    GstElement* audioCapsfilter = gst_element_factory_make("capsfilter", "audioCapsfilter");
    GstElement* audioDec = gst_element_factory_make("opusdec", "audioDec");
    GstElement* audioDepay = gst_element_factory_make("rtpopusdepay", "audioDepay");
    GstElement* audioConv = gst_element_factory_make("audioconvert", "audioConv");
    GstElement* audioSink = gst_element_factory_make("autoaudiosink", "audioSink");

    // Add element to pipeline
    gst_bin_add_many(GST_BIN(videoPipeline), videoSrc, videoCapsfilter, videoDepay, videoDec, videoSink, NULL);
    gst_bin_add_many(GST_BIN(audioPipeline), audioSrc, audioCapsfilter, audioDec, audioDepay, audioConv, audioSink, NULL);

    // linking elements
    gst_element_link_many(videoSrc, videoCapsfilter, videoDepay, videoDec, videoSink, NULL);
    gst_element_link_many(audioSrc, audioCapsfilter, audioDepay, audioDec, audioConv, audioSink, NULL);

    // Receive port setting
    g_object_set(videoSrc, "port", 5001, NULL);
    g_object_set(audioSrc, "port", 5002, NULL);

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
        return -1;
    }

    // Run main loop
    GstBus* bus = gst_element_get_bus(videoPipeline);
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
    gst_element_set_state(videoPipeline, GST_STATE_NULL);
    gst_element_set_state(audioPipeline, GST_STATE_NULL);
    gst_object_unref(videoPipeline);
    gst_object_unref(audioPipeline);
    return 0;
}
