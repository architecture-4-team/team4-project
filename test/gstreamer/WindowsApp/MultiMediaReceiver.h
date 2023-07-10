#pragma once
#ifndef MULTIMEDIARECEIVER_H
#define MULTIMEDIARECEIVER_H

#include <gst/gst.h>
#include <iostream>
#include <Windows.h>
#include "MultimediaInterface.h"

typedef struct ssrcData
{
	guint32 ssrcValue1;
	guint32 ssrcValue2;
	guint32 ssrcValue3;
}SSRC_DATA_T;


class MultimediaReceiver : public MultimediaInterface {
public:
    MultimediaReceiver();
    ~MultimediaReceiver();
    bool initialize();
    void cleanup();
    void start();
    void stop();
    void setPort(int videoPort, int audioPort);
    void setWindow(void* hVideo);
    bool runThread();	
    void setWindow(void* hVideo1, void* hVideo2, void* hVideo3);

    void setJitterBuffer(int latency);
    void setRTP();
    void setId(int id) { this->id = id; };
    int getId() { return id; };
    int getTotalReceiver() { return receieverNumbers; };
    
    void changeState(int state); // debug
	SSRC_DATA_T *ssrcTemp;
private:
    // Pipeline
    GstElement* receiverVideoPipeline;
    GstElement* receiverAudioPipeline;

    GstElement* jitterbufferVideo;

    GstElement* videoSrc;

    GstElement* videoCapsfilter1;
    GstElement* videoDepay1;
    GstElement* videoDec1;
    GstElement* videoSink1;

    GstElement* videoCapsfilter2;
    GstElement* videoDepay2;
    GstElement* videoDec2;
    GstElement* videoSink2;

    GstElement* videoCapsfilter3;
    GstElement* videoDepay3;
    GstElement* videoDec3;
    GstElement* videoSink3;

    GstElement* tee;

    GstElement* queue1;
    GstElement* queue2;
    GstElement* queue3;

    GstPad* tee_pad1, *tee_pad2, *tee_pad3;
    GstPad* queue_pad1, *queue_pad2, *queue_pad3;
    
    GstElement* audioSrc;
    GstElement* audioCapsfilter;
    GstElement* jitterbufferAudio;
    GstElement* audioDec;
    GstElement* audioDepay;
    GstElement* audioConv;
    GstElement* audioSink;

    GstBus* receiverVideoBus;
    GstBus* receiverAudioBus;

    GMainLoop* receiverLoop;

    int id; // °´Ã¼ÀÇ id
    static int receieverNumbers;

    HANDLE hThread; // Sender Thread
    static DWORD WINAPI threadCallback(LPVOID lpParam);

    bool initialized;
};

static GstPadProbeReturn probe_callback_videoDepay1(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);
static GstPadProbeReturn probe_callback_videoDepay2(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);
static GstPadProbeReturn probe_callback_videoDepay3(GstPad* pad, GstPadProbeInfo* info, gpointer user_data);
#endif  // MULTIMEDIARECEIVER_H