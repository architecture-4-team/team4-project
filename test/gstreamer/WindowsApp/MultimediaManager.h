#pragma once
#ifndef MULTIMEDIAMANAGER_H
#define MULTIMEDIAMANAGER_H

#include <mutex>
#include <vector>
#include "MultimediaInterface.h"
#include <unordered_map>

class MultimediaManager {
public:
    static MultimediaManager& GetInstance();
    ~MultimediaManager();

    bool initialize();
    bool initialize(void* hVideo);
    bool acceptCall(/* Callee 객체 받기 */void* hVideo);
    bool acceptCall(/* Callee 객체 받기 */void* hVideo, int videoPort, int audioPort);
    void makeCall();
    void pauseCall();
private:
    MultimediaManager();
    MultimediaManager(const MultimediaManager&) = delete;

    void SenderInitialize(void* hVideo);

    MultimediaManager& operator=(const MultimediaManager&) = delete;

    static std::mutex instanceMutex;  // 인스턴스 생성 동기화에 사용할 뮤텍스

    MultimediaInterface& mSender;
    std::vector<MultimediaInterface*> receiverList;
    std::unordered_map<int, MultimediaInterface*> receiverMap;
};
#endif // MULTIMEDIAMANAGER_H
