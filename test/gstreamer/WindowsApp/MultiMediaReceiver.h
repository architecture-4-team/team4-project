#pragma once
#ifndef MULTIMEDIARECEIVER_H
#define MULTIMEDIARECEIVER_H

#include <gst/gst.h>
#include <iostream>

class MultimediaReceiver {
public:
    MultimediaReceiver();
    ~MultimediaReceiver();
    bool initialize();
    void cleanup();
    void startReceiver();
    void stopReceiver();
    void setPort(int videoPort, int audioPort);
    void setJitterBuffer(int latency);
    void setRTP();
private:
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
    GMainLoop* receiverLoop;
};

#endif  // MULTIMEDIARECEIVER_H