#pragma once
#ifndef MULTIMEDIAMANAGER_H
#define MULTIMEDIAMANAGER_H

#include <mutex>
#include <vector>
#include "MultimediaInterface.h"

class MultimediaManager {
public:
    static MultimediaManager& GetInstance() {
        // ��Ƽ������ ȯ�濡�� ������ �ν��Ͻ� ������ �����ϱ� ���� ����ȭ
        std::lock_guard<std::mutex> lock(instanceMutex);
        static MultimediaManager instance;
        return instance;
    }
    ~MultimediaManager();

    bool initialize();

private:
    MultimediaManager();
    MultimediaManager(const MultimediaManager&) = delete;
    MultimediaManager& operator=(const MultimediaManager&) = delete;

    static std::mutex instanceMutex;  // �ν��Ͻ� ���� ����ȭ�� ����� ���ؽ�

    MultimediaInterface& mSender;
    std::vector<MultimediaInterface*> receiverList;
};
#endif // MULTIMEDIAMANAGER_H
