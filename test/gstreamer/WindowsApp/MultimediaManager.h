#pragma once
#ifndef MULTIMEDIAMANAGER_H
#define MULTIMEDIAMANAGER_H

#include <mutex>
#include <vector>
#include <unordered_map>

#include "MultimediaInterface.h"

class MultimediaManager {
public:
    static MultimediaManager& GetInstance();
    ~MultimediaManager();

    // bool initialize(); // not used for now
    bool setupSender(void* hVideo, std::string ip, int videoPort, int audioPort);
    bool setupReceiver(void* hVideo, int videoPort, int audioPort, int id);
    bool setupReceiver(void* hVideo1, void* hVideo2, void* hVideo3, int videoPort, int audioPort, int id);
    void makeCall();
    void pauseCall();
    bool acceptCall(/* Callee ��ü �ޱ� */void* hVideo); // not used for now
    void endCall();

    void pauseReceiver(int video); //debug
    void playReceiver(int video); // debug

    void makeReceiverStateChange(int video, int state); // debug
private:
    MultimediaManager();
    MultimediaManager(const MultimediaManager&) = delete;

    MultimediaManager& operator=(const MultimediaManager&) = delete;

    static std::mutex instanceMutex;  // �ν��Ͻ� ���� ����ȭ�� ����� ���ؽ�

    MultimediaInterface& mSender;
    //std::vector<MultimediaInterface*> receiverList;
    std::unordered_map<int, MultimediaInterface*> receiverMap;

    
};
#endif // MULTIMEDIAMANAGER_H
