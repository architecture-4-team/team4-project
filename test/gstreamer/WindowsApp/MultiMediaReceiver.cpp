#include "MultiMediaReceiver.h"
#include <gst/gst.h>
#include <gst/video/videooverlay.h>
#include <gst/rtp/gstrtpbuffer.h>


static gboolean handle_receiver_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data);
static gboolean handle_receiver_audio_bus_message(GstBus* bus, GstMessage* msg, gpointer data);

static GstPadProbeReturn probe_callback(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);

int MultimediaReceiver::receieverNumbers = 0;

MultimediaReceiver::MultimediaReceiver()
    : receiverVideoPipeline(nullptr), receiverAudioPipeline(nullptr),
    videoSrc(nullptr), audioSrc(nullptr), audioCapsfilter(nullptr),
    jitterbufferAudio(nullptr), audioDec(nullptr), audioDepay(nullptr),
    audioConv(nullptr), audioSink(nullptr), receiverVideoBus(nullptr),
    receiverLoop(nullptr), initialized(false)
{
    receieverNumbers += 1;

    // Initialize GStreamer only one time at initialization of program
    // gst_init(nullptr, nullptr);
}

MultimediaReceiver::~MultimediaReceiver()
{
    cleanup();
    // gst_deinit(); - do not deinit for receiver object destruction
}

bool MultimediaReceiver::initialize()
{
    if (initialized) return true;

    // Create receiver video pipeline
    receiverVideoPipeline = gst_pipeline_new("receiverVideoPipeline");

    // Create video elements
    videoSrc = gst_element_factory_make("udpsrc", "videoSrc");

    tee = gst_element_factory_make("tee", "tee");

    queue1 = gst_element_factory_make("queue", "queue1");
    videoCapsfilter1 = gst_element_factory_make("capsfilter", "videoCapsfilter1");
    videoDepay1 = gst_element_factory_make("rtph264depay", "videoDepay1");
    videoDec1 = gst_element_factory_make("avdec_h264", "videoDec1");
    videoSink1 = gst_element_factory_make("d3dvideosink", "videoSink1");

    queue2 = gst_element_factory_make("queue", "queue2");
    videoCapsfilter2 = gst_element_factory_make("capsfilter", "videoCapsfilter2");
    videoDepay2 = gst_element_factory_make("rtph264depay", "videoDepay");
    videoDec2 = gst_element_factory_make("avdec_h264", "videoDec");
    videoSink2 = gst_element_factory_make("d3dvideosink", "videoSink");

    queue3 = gst_element_factory_make("queue", "queue3");
    videoCapsfilter3 = gst_element_factory_make("capsfilter", "videoCapsfilter3");
    videoDepay3 = gst_element_factory_make("rtph264depay", "videoDepa3");
    videoDec3 = gst_element_factory_make("avdec_h264", "videoDe3");
    videoSink3 = gst_element_factory_make("d3dvideosink", "videoSin3");

    // Create receiver audio pipeline
    receiverAudioPipeline = gst_pipeline_new("receiverAudioPipeline");

    // Create audio elements
    audioSrc = gst_element_factory_make("udpsrc", "audioSrc");
    audioCapsfilter = gst_element_factory_make("capsfilter", "audioCapsfilter");
    jitterbufferAudio = gst_element_factory_make("rtpjitterbuffer", "jitterbufferAudio");
    audioDec = gst_element_factory_make("opusdec", "audioDec");
    audioDepay = gst_element_factory_make("rtpopusdepay", "audioDepay");
    audioConv = gst_element_factory_make("audioconvert", "audioConv");
    audioSink = gst_element_factory_make("autoaudiosink", "audioSink");

    // Check if all elements are created successfully
    if (!receiverVideoPipeline || !receiverAudioPipeline || !videoSrc || !tee ||
        !queue1 || !videoCapsfilter1 || !videoDepay1 || !videoDec1 || !videoSink1 ||
        !queue2 || !videoCapsfilter2 || !videoDepay2 || !videoDec2 || !videoSink2 ||
        !queue3 || !videoCapsfilter3 || !videoDepay3 || !videoDec3 || !videoSink3 ||
        !audioSrc || !audioCapsfilter || !jitterbufferAudio || !audioDec || !audioDepay || !audioConv || !audioSink)
    {
        std::cerr << "Failed to create GStreamer elements." << std::endl;
        cleanup();
        return false;
    }

    // 요소를 파이프라인에 추가
    gst_bin_add_many(GST_BIN(receiverVideoPipeline), videoSrc, tee, 
        queue1, videoCapsfilter1, videoDepay1, videoDec1, videoSink1,
        queue2, videoCapsfilter2, videoDepay2, videoDec2, videoSink2,
        queue3, videoCapsfilter3, videoDepay3, videoDec3, videoSink3, NULL);

    // 요소 연결
    gst_element_link(videoSrc, tee);

    // Tee와 큐 연결
    tee_pad1 = gst_element_request_pad_simple(tee, "src_%u");
    queue_pad1 = gst_element_get_static_pad(queue1, "sink");
    tee_pad2 = gst_element_request_pad_simple(tee, "src_%u");
    queue_pad2 = gst_element_get_static_pad(queue2, "sink");
    tee_pad3 = gst_element_request_pad_simple(tee, "src_%u");
    queue_pad3 = gst_element_get_static_pad(queue3, "sink");
    
    if (gst_pad_link(tee_pad1, queue_pad1) != GST_PAD_LINK_OK ||
        gst_pad_link(tee_pad2, queue_pad2) != GST_PAD_LINK_OK || 
        gst_pad_link(tee_pad3, queue_pad3) != GST_PAD_LINK_OK) {
        g_printerr("Tee could not be linked.\n");
        gst_object_unref(receiverVideoPipeline);
        return 0;
    }
    gst_object_unref(tee_pad1);
    gst_object_unref(tee_pad2);
    gst_object_unref(tee_pad3);

    gst_element_link_many(queue1, videoCapsfilter1, videoDepay1, videoDec1, videoSink1, NULL);
    gst_element_link_many(queue2, videoCapsfilter2, videoDepay2, videoDec2, videoSink2, NULL);
    gst_element_link_many(queue3, videoCapsfilter3, videoDepay3, videoDec3, videoSink3, NULL);

    // Link audio elements
    gst_element_link_many(audioSrc, audioCapsfilter, jitterbufferAudio, audioDepay, audioDec, audioConv, audioSink, nullptr);

    // Get the bus for the pipelines
    receiverVideoBus = gst_element_get_bus(receiverVideoPipeline);
    receiverAudioBus = gst_element_get_bus(receiverAudioPipeline);

    // Add watch to the bus to handle messages
    gst_bus_add_watch(receiverVideoBus, (GstBusFunc)handle_receiver_video_bus_message, this);
    gst_bus_add_watch(receiverAudioBus, (GstBusFunc)handle_receiver_audio_bus_message, this);

    // Get the sink pad of the sink element
	GstPad* Pad1 = gst_element_get_static_pad(videoCapsfilter1, "sink");
	gst_pad_add_probe(Pad1, GST_PAD_PROBE_TYPE_BUFFER, (GstPadProbeCallback)probe_callback_videoDepay1, NULL, NULL);
#if 1
	GstPad* Pad2 = gst_element_get_static_pad(videoCapsfilter2, "sink");
	gst_pad_add_probe(Pad2, GST_PAD_PROBE_TYPE_BUFFER, (GstPadProbeCallback)probe_callback_videoDepay2, NULL, NULL);
	GstPad* Pad3 = gst_element_get_static_pad(videoCapsfilter3, "sink");
	gst_pad_add_probe(Pad3, GST_PAD_PROBE_TYPE_BUFFER, (GstPadProbeCallback)probe_callback_videoDepay3, NULL, NULL);
#endif 
    GstPad* pad = gst_element_get_static_pad(videoCapsfilter1, "sink");
    gst_pad_add_probe(pad, GST_PAD_PROBE_TYPE_BUFFER, (GstPadProbeCallback)probe_callback, this, NULL);

    /* ToDo : shall be discussed */
    this->setJitterBuffer(50);
    this->setRTP();

    initialized = true;

    return true;
}

void MultimediaReceiver::cleanup()
{
    // Cleanup the main loop
    g_main_loop_unref(receiverLoop);
    receiverLoop = nullptr;

    if (receiverVideoPipeline)
    {
        gst_element_set_state(receiverVideoPipeline, GST_STATE_NULL);
        gst_object_unref(receiverVideoPipeline);
        receiverVideoPipeline = nullptr;
    }

    if (receiverAudioPipeline)
    {
        gst_element_set_state(receiverAudioPipeline, GST_STATE_NULL);
        gst_object_unref(receiverAudioPipeline);
        receiverAudioPipeline = nullptr;
    }

    // Release video elements
    gst_object_unref(videoSrc);

    // Release audio elements
    gst_object_unref(audioSrc);
    gst_object_unref(audioCapsfilter);
    gst_object_unref(jitterbufferAudio);
    gst_object_unref(audioDec);
    gst_object_unref(audioDepay);
    gst_object_unref(audioConv);
    gst_object_unref(audioSink);

    // Release video bus
    if (receiverVideoBus)
    {
        gst_object_unref(receiverVideoBus);
        receiverVideoBus = nullptr;
    }

    // Release audio bus
    if (receiverAudioBus)
    {
        gst_object_unref(receiverAudioBus);
        receiverAudioBus = nullptr;
    }

    initialized = false;
}

void MultimediaReceiver::start()
{
    if (receiverVideoPipeline)
        gst_element_set_state(receiverVideoPipeline, GST_STATE_PLAYING);

    if (receiverAudioPipeline)
        gst_element_set_state(receiverAudioPipeline, GST_STATE_PLAYING);

    if (!receiverLoop) {
        // Create a GMainLoop to handle events
        receiverLoop = g_main_loop_new(nullptr, FALSE);
    }
    // Run the main loop
    g_main_loop_run(receiverLoop);

}

void MultimediaReceiver::stop()
{
    if (receiverVideoPipeline)
        gst_element_set_state(receiverVideoPipeline, GST_STATE_NULL);

    if (receiverAudioPipeline)
        gst_element_set_state(receiverAudioPipeline, GST_STATE_NULL);

    // Quit the main loop
    g_main_loop_quit(receiverLoop);
}

void MultimediaReceiver::setPort(int videoPort, int audioPort)
{
    g_object_set(G_OBJECT(videoSrc), "port", videoPort, nullptr);
    g_object_set(G_OBJECT(audioSrc), "port", audioPort, nullptr);
}

// 쓰레드 함수
DWORD WINAPI MultimediaReceiver::threadCallback(LPVOID lpParam)
{
    // 쓰레드에서 실행할 로직을 작성합니다.
    MultimediaReceiver* pReceiver = static_cast<MultimediaReceiver*>(lpParam);

    pReceiver->start();

    WaitForSingleObject(pReceiver->hThread, INFINITE);
    CloseHandle(pReceiver->hThread);
    pReceiver->hThread = INVALID_HANDLE_VALUE;
    return 0;
}

bool MultimediaReceiver::runThread()
{
    hThread = CreateThread(NULL, 0, MultimediaReceiver::threadCallback, this, 0, NULL);
    if (hThread)
    {
        CloseHandle(hThread);  // 쓰레드 핸들 닫기
    }
    return true;
}

void MultimediaReceiver::setJitterBuffer(int latency)
{
    // latency: 지터 버퍼의 대기 시간(밀리초)을 설정합니다. 이 값은 네트워크 지연을 허용하는 최대 시간을 나타냅니다. 기본값은 200ms입니다.
    // drop - on - latency: 이 속성이 true로 설정되면, 지터 버퍼는 대기 시간 초과 패킷을 버립니다.기본값은 false입니다.
    g_object_set(G_OBJECT(jitterbufferVideo), "latency", latency, "do-lost", TRUE, NULL);
    g_object_set(G_OBJECT(jitterbufferAudio), "latency", latency, "do-lost", TRUE, NULL);
}

void MultimediaReceiver::setRTP()
{
    // RTP video format (caps) settings
    GstCaps* videoCaps1 = gst_caps_from_string("application/x-rtp, media=(string)video, payload=(int)96");
    g_object_set(G_OBJECT(videoCapsfilter1), "caps", videoCaps1, NULL);
    gst_caps_unref(videoCaps1);

    GstCaps* videoCaps2 = gst_caps_from_string("application/x-rtp, media=(string)video, payload=(int)96");
    g_object_set(G_OBJECT(videoCapsfilter2), "caps", videoCaps2, NULL);
    gst_caps_unref(videoCaps2);

    GstCaps* videoCaps3 = gst_caps_from_string("application/x-rtp, media=(string)video, payload=(int)96");
    g_object_set(G_OBJECT(videoCapsfilter3), "caps", videoCaps3, NULL);
    gst_caps_unref(videoCaps3);

    // RTP audio format (caps) settings
    GstCaps* audioCaps = gst_caps_from_string("application/x-rtp, media=(string)audio, encoding-name=OPUS,  payload=(int)96");
    g_object_set(G_OBJECT(audioCapsfilter), "caps", audioCaps, NULL);
    gst_caps_unref(audioCaps);
}

void MultimediaReceiver::setWindow(void* hVideo) {
    // VideoDisplaySink를 윈도우와 연결
     // 비디오 출력 설정
    g_object_set(G_OBJECT(videoSink1), "force-aspect-ratio", TRUE, NULL);

    // 비디오 오버레이 설정
    gst_video_overlay_set_window_handle(GST_VIDEO_OVERLAY(videoSink1), (guintptr)hVideo);
}


void MultimediaReceiver::setWindow(void* hVideo1, void* hVideo2, void* hVideo3)
{
    // VideoDisplaySink를 윈도우와 연결
     // 비디오 출력 설정
    g_object_set(G_OBJECT(videoSink1), "force-aspect-ratio", TRUE, NULL);

    // 비디오 오버레이 설정
    gst_video_overlay_set_window_handle(GST_VIDEO_OVERLAY(videoSink1), (guintptr)hVideo1);

    // 비디오 출력 설정
    g_object_set(G_OBJECT(videoSink2), "force-aspect-ratio", TRUE, NULL);

    // 비디오 오버레이 설정
    gst_video_overlay_set_window_handle(GST_VIDEO_OVERLAY(videoSink2), (guintptr)hVideo2);

    // 비디오 출력 설정
    g_object_set(G_OBJECT(videoSink3), "force-aspect-ratio", TRUE, NULL);

    // 비디오 오버레이 설정
    gst_video_overlay_set_window_handle(GST_VIDEO_OVERLAY(videoSink3), (guintptr)hVideo3);

}

void MultimediaReceiver::changeState(int state)
{
    if (receiverVideoPipeline)
        gst_element_set_state(receiverVideoPipeline, (GstState)state);

    if (receiverAudioPipeline)
        gst_element_set_state(receiverAudioPipeline, (GstState)state);

}

static gboolean handle_receiver_video_bus_message(GstBus* bus, GstMessage* msg, gpointer data)
{
    MultimediaReceiver* receiver = static_cast<MultimediaReceiver*>(data);

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
        receiver->stop(); // Quit the main loop in case of an error
        break;
    }
    case GST_MESSAGE_EOS:
        g_print("End-Of-Stream reached.\n");
        receiver->stop(); // Quit the main loop when the end of the stream is reached
        break;
    case GST_MESSAGE_STATE_CHANGED:
    {
        GstState old_state, new_state, pending_state;
        gst_message_parse_state_changed(msg, &old_state, &new_state, &pending_state);
        g_print("Receiver %d Video state changed from %s to %s\n", receiver->getId(), gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));
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

static gboolean handle_receiver_audio_bus_message(GstBus* bus, GstMessage* msg, gpointer data)
{
    MultimediaReceiver* receiver = static_cast<MultimediaReceiver*>(data);

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
        receiver->stop(); // Quit the main loop in case of an error
        break;
    }
    case GST_MESSAGE_EOS:
        g_print("End-Of-Stream reached.\n");
        receiver->stop(); // Quit the main loop when the end of the stream is reached
        break;
    case GST_MESSAGE_STATE_CHANGED:
    {
        GstState old_state, new_state, pending_state;
        gst_message_parse_state_changed(msg, &old_state, &new_state, &pending_state);
        g_print("Receiver %d Audio state changed from %s to %s\n", receiver->getId(), gst_element_state_get_name(old_state), gst_element_state_get_name(new_state));
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

static GstPadProbeReturn probe_callback(GstPad* pad, GstPadProbeInfo* info, gpointer user_data)
{
    MultimediaReceiver* receiver = static_cast<MultimediaReceiver*>(user_data);
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

        //g_print("Receive %d Data Rate: %lu bps\n", receiver->getId(), dataRate);

        totalBuffer = 0;
        prevTimestamp = timestamp;
    }

    return GST_PAD_PROBE_OK;
}

static GstPadProbeReturn probe_callback_videoDepay1(GstPad* pad, GstPadProbeInfo* info, gpointer user_data)
{
    GstBuffer* buffer = GST_PAD_PROBE_INFO_BUFFER(info);
    guint64 timestamp = GST_BUFFER_TIMESTAMP(buffer);
    static guint64 prevTimestamp = 0;

	GstRTPBuffer rtp_buffer;
	guint32 ssrc = 0;
	guint32 targetssrc = 0xABCD1234;
	static guint32 prev_ssrc = 0;

	if(buffer)
	{
		if(gst_rtp_buffer_map(buffer, GST_MAP_READ, &rtp_buffer))
		{
			ssrc = gst_rtp_buffer_get_ssrc(&rtp_buffer);

			guint64 durationNs = timestamp - prevTimestamp;
			
			if (durationNs > GST_SECOND)
			{
				g_print("SSRC1: 0x%08x/0x%08x\n", ssrc, targetssrc);
				prevTimestamp = timestamp;
			}

#if 1
			if (ssrc == targetssrc)
			{				
				return GST_PAD_PROBE_OK;
			}
			else 
			{
				return GST_PAD_PROBE_DROP;
			}
#endif
			prev_ssrc = ssrc;
		}
	}
	
    return GST_PAD_PROBE_OK;
}

static GstPadProbeReturn probe_callback_videoDepay2(GstPad* pad, GstPadProbeInfo* info, gpointer user_data)
{
    GstBuffer* buffer = GST_PAD_PROBE_INFO_BUFFER(info);
    guint64 timestamp = GST_BUFFER_TIMESTAMP(buffer);
    static guint64 prevTimestamp = 0;

	GstRTPBuffer rtp_buffer;
	guint32 ssrc = 0;
	guint32 targetssrc = 0xABCD1230;
	static guint32 prev_ssrc = 0;

	if(buffer)
	{
		if(gst_rtp_buffer_map(buffer, GST_MAP_READ, &rtp_buffer))
		{
			ssrc = gst_rtp_buffer_get_ssrc(&rtp_buffer);

			guint64 durationNs = timestamp - prevTimestamp;
			
			if (durationNs > GST_SECOND)
			{
				g_print("SSRC2: 0x%08x/0x%08x\n", ssrc, targetssrc);
				prevTimestamp = timestamp;
			}

#if 1
			if (ssrc == targetssrc)
			{				
				return GST_PAD_PROBE_OK;
			}
			else 
			{
				return GST_PAD_PROBE_DROP;
			}
#endif
			prev_ssrc = ssrc;
		}
	}
	
    return GST_PAD_PROBE_OK;
}

static GstPadProbeReturn probe_callback_videoDepay3(GstPad* pad, GstPadProbeInfo* info, gpointer user_data)
{
    GstBuffer* buffer = GST_PAD_PROBE_INFO_BUFFER(info);
    guint64 timestamp = GST_BUFFER_TIMESTAMP(buffer);
    static guint64 prevTimestamp = 0;

	GstRTPBuffer rtp_buffer;
	guint32 ssrc = 0;
	guint32 targetssrc = 0xABCD1233;
	static guint32 prev_ssrc = 0;

	if(buffer)
	{
		if(gst_rtp_buffer_map(buffer, GST_MAP_READ, &rtp_buffer))
		{
			ssrc = gst_rtp_buffer_get_ssrc(&rtp_buffer);

			guint64 durationNs = timestamp - prevTimestamp;
			
			if (durationNs > GST_SECOND)
			{
				g_print("SSRC3: 0x%08x/0x%08x\n", ssrc, targetssrc);
				prevTimestamp = timestamp;
			}

#if 1
			if (ssrc == targetssrc)
			{				
				return GST_PAD_PROBE_OK;
			}
			else 
			{
				return GST_PAD_PROBE_DROP;
			}
#endif
			prev_ssrc = ssrc;
		}
	}
	
    return GST_PAD_PROBE_OK;
}

