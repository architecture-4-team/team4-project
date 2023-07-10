#pragma once
#ifndef MULTIMEDIASENDER_H
#define MULTIMEDIASENDER_H

#include <mutex>
#include <gst/gst.h>
#include <Windows.h>
#include "MultimediaInterface.h"

class MultimediaSender : public MultimediaInterface
{
public:
    static MultimediaSender& GetInstance() {
        // ��Ƽ������ ȯ�濡�� ������ �ν��Ͻ� ������ �����ϱ� ���� ����ȭ
        std::lock_guard<std::mutex> lock(instanceMutex);

        static MultimediaSender instance;
        return instance;
    }

    ~MultimediaSender();

    bool initialize();
    void cleanup();
    void start();
    void stop();
    void setPort(int videoPort, int audioPort);
    void setWindow(void* hVideo);
    bool runThread();

    void setVideoResolution();
	void setSSRC(int ssrcFromServer);
	std::string getReceiverIP();
    void setReceiverIP(std::string ip);
    void setCameraIndex(int index);
    void setVideoFlipMethod(int method);
	void setVideoEncBitRate();
    void setVideoEncTune();
    void setAudioOpusencAudioType(int audioType);

private:
    MultimediaSender();
    MultimediaSender(const MultimediaSender&) = delete;
    MultimediaSender& operator=(const MultimediaSender&) = delete;

    static std::mutex instanceMutex;  // �ν��Ͻ� ���� ����ȭ�� ����� ���ؽ�

    bool initialized;
    std::string receiverIp;

	unsigned int sendVideoWidth		= 320;
	unsigned int sendVideoHeight	= 240;

	unsigned int sendVideoBitRate	= 512;	//(x264 codec)default : 2048
	unsigned int sendVideoTune		= 0x4;	//(x264 codec)(bitwise) 0x1: still image, 0x2: Fast Decode, 0x4: zero latency
	
    GstElement* senderVideoPipeline;
    GstElement* senderAudioPipeline;

    GstElement* videoSrc;
	GstElement* rtpsource;
    GstElement* videoFlip;
    GstElement* videoCapsfilter;
    GstElement* videoEnc;
    GstElement* videoPay;
    GstElement* videoSink;
    GstElement* tee;
    GstElement* queueDisplay;
    GstElement* queueNetwork;
    GstElement* videoDisplaySink;
    GstElement* videoSinkWindow;

    GstElement* audioSrc;
    GstElement* audioConv;
    GstElement* audioResample;
    GstElement* audioOpusenc;
    GstElement* audioPay;
    GstElement* audioSink;

    GstBus* senderVideoBus;
    GstBus* senderAudioBus;

    GMainLoop* mainLoop;

    HANDLE hThread; // Sender Thread
    static DWORD WINAPI threadCallback(LPVOID lpParam);
};

#endif  // MULTIMEDIA_SENDER_H
