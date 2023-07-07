#pragma once
#ifndef MULTIMEDIARECEIVER_H
#define MULTIMEDIARECEIVER_H

#include <gst/gst.h>
#include <iostream>
#include "MultimediaInterface.h"

class MultimediaReceiver : public MultimediaInterface {
public:
    MultimediaReceiver();
    ~MultimediaReceiver();
    bool initialize();
    void cleanup();
    void start();
    void stop();
    void setPort(int videoPort, int audioPort);
    void setJitterBuffer(int latency);
    void setRTP();
    void setWindow(void* hVideo);

    void setId(int id) { this->id = id; };
    int getId() { return id; };
    int getTotalReceiver() { return receieverNumbers; };
private:
    // Pipeline
    GstElement* receiverVideoPipeline;
    GstElement* receiverAudioPipeline;

    GstElement* videoSrc;
    GstElement* videoCapsfilter;
    GstElement* jitterbufferVideo;
    GstElement* videoDepay;
    GstElement* videoDec;
    GstElement* videoSink;
    
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
};

#endif  // MULTIMEDIARECEIVER_H