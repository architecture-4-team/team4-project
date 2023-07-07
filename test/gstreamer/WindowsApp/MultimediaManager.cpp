#include "multimediaManager.h"
#include "MultimediaSender.h"
#include "MultimediaReceiver.h"

std::mutex MultimediaManager::instanceMutex;

MultimediaManager& MultimediaManager::GetInstance() {
    // 멀티스레드 환경에서 안전한 인스턴스 생성을 보장하기 위해 동기화
    std::lock_guard<std::mutex> lock(instanceMutex);
    static MultimediaManager instance;
    return instance;
}

MultimediaManager::MultimediaManager() 
    : mSender(MultimediaSender::GetInstance()), receiverList(0, nullptr)
{

};

MultimediaManager::~MultimediaManager() {
    mSender.stop();
    mSender.cleanup();
}

void MultimediaManager::SenderInitialize(void* hVideo) {
    // Initialize sender pipelines
    if (!mSender.initialize())
    {
//        std::cerr << "Failed to initialize sender pipelines." << std::endl;
//        return 1;
    }

    // Set video resolution
    dynamic_cast<MultimediaSender&>(mSender).setVideoResolution();

    // Set receiver IP and port
    dynamic_cast<MultimediaSender&>(mSender).setReceiverIP();
    dynamic_cast<MultimediaSender&>(mSender).setPort(10001, 10002);

    // Set camera index (if necessary)
    dynamic_cast<MultimediaSender&>(mSender).setCameraIndex(0);

    // Set video flip method (if necessary)
    dynamic_cast<MultimediaSender&>(mSender).setVideoFlipMethod(4); // Horizontal flip

    // Set video encoding tune (if necessary)
    dynamic_cast<MultimediaSender&>(mSender).setVideoEncTune();
    dynamic_cast<MultimediaSender&>(mSender).setVideoEncBitRate();

    // Set audio encoding type (if necessary)
    dynamic_cast<MultimediaSender&>(mSender).setAudioOpusencAudioType(2051); // Restricted low delay

    mSender.setWindow(hVideo);
}

bool MultimediaManager::initialize(void* hVideo) {

    mSender = MultimediaSender::GetInstance();

    SenderInitialize(hVideo);

    return true;
}

bool MultimediaManager::acceptCall(/* Callee 객체 받기 */void* hVideo)
{
    MultimediaReceiver* receiver = new MultimediaReceiver(); // MultimediaReceiver 객체 생성
    receiverList.push_back(receiver);

    if (!receiver->initialize())
    {
        std::cerr << "Failed to initialize MultimediaReceiver." << std::endl;
        return -1;
    }
    receiver->setPort(10001, 10002);     // Set receive port

    int id = receiver->getTotalReceiver();
    receiver->setId(id);

    receiver->setWindow(hVideo);       // Set window handle to show window

    return true;
}

bool MultimediaManager::acceptCall(/* Callee 객체 받기 */void* hVideo, int videoPort, int audioPort)
{
    MultimediaReceiver* receiver = new MultimediaReceiver(); // MultimediaReceiver 객체 생성
    receiverList.push_back(receiver);

    if (!receiver->initialize())
    {
        std::cerr << "Failed to initialize MultimediaReceiver." << std::endl;
        return -1;
    }
    receiver->setPort(videoPort, audioPort);     // Set receive port

    int id = receiver->getTotalReceiver();
    receiver->setId(id);

    receiver->setWindow(hVideo);       // Set window handle to show window
    
    return true;
}

void MultimediaManager::makeCall()
{
    mSender.start();
}

void MultimediaManager::pauseCall()
{
    mSender.stop();
}