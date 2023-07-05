// WindowsApp.cpp : 애플리케이션에 대한 진입점을 정의합니다.
//

#include "framework.h"
#include "WindowsApp.h"
#include <Commctrl.h>
#include <Windows.h>
#include <gst/gst.h>
#include <stdio.h>
#include <gst/gst.h>

#include "MultimediaSender.h"
#include "MultimediaReceiver.h"
#include "MultimediaInterface.h"
#include "global_setting.h"

#define MAX_LOADSTRING 100

// functions
LRESULT OnSize(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
RECT getWinSize(HWND hWnd);
static LRESULT OnCreate(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
DWORD WINAPI RunSENDER(LPVOID lpParam);
DWORD WINAPI RunRECEIVER(LPVOID lpParam);
static void SetStdOutToNewConsole(void);

static void stopSENDER();
static void stopRECEIVER();

// 전역 변수:
HINSTANCE hInst;                                // 현재 인스턴스입니다.
WCHAR szTitle[MAX_LOADSTRING];                  // 제목 표시줄 텍스트입니다.
WCHAR szWindowClass[MAX_LOADSTRING];            // 기본 창 클래스 이름입니다.

static FILE* pCout = NULL;

HWND hWndMain;

HANDLE hSenderThread;
HANDLE hReceiverThread;

MultimediaInterface* mSender = new MultimediaSender();
MultimediaInterface* mReceiver = new MultimediaReceiver();

HWND videoWindow0; // Video 출력용 윈도우 핸들
HWND videoWindow1; // Video 출력용 윈도우 핸들

// 이 코드 모듈에 포함된 함수의 선언을 전달합니다:
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    About(HWND, UINT, WPARAM, LPARAM);

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(lpCmdLine);

    // TODO: 여기에 코드를 입력합니다.
    SetStdOutToNewConsole();

    // Initialize GStreamer
    gst_init(NULL, NULL);

    // 전역 문자열을 초기화합니다.
    LoadStringW(hInstance, IDS_APP_TITLE, szTitle, MAX_LOADSTRING);
    LoadStringW(hInstance, IDC_WINDOWSAPP, szWindowClass, MAX_LOADSTRING);
    MyRegisterClass(hInstance);

    // 애플리케이션 초기화를 수행합니다:
    if (!InitInstance (hInstance, nCmdShow))
    {
        return FALSE;
    }

    HACCEL hAccelTable = LoadAccelerators(hInstance, MAKEINTRESOURCE(IDC_WINDOWSAPP));

    MSG msg;

    // 기본 메시지 루프입니다:
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        if (!TranslateAccelerator(msg.hwnd, hAccelTable, &msg))
        {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
    return (int) msg.wParam;
}



//
//  함수: MyRegisterClass()
//
//  용도: 창 클래스를 등록합니다.
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex;

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = WndProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hIcon          = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_WINDOWSAPP));
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+1);
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_WINDOWSAPP);
    wcex.lpszClassName  = szWindowClass;
    wcex.hIconSm        = LoadIcon(wcex.hInstance, MAKEINTRESOURCE(IDI_SMALL));

    return RegisterClassExW(&wcex);
}

//
//   함수: InitInstance(HINSTANCE, int)
//
//   용도: 인스턴스 핸들을 저장하고 주 창을 만듭니다.
//
//   주석:
//
//        이 함수를 통해 인스턴스 핸들을 전역 변수에 저장하고
//        주 프로그램 창을 만든 다음 표시합니다.
//
BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   hInst = hInstance; // 인스턴스 핸들을 전역 변수에 저장합니다.

   HWND hWnd = CreateWindowW(szWindowClass, szTitle, WS_OVERLAPPEDWINDOW,
      CW_USEDEFAULT, 0, CW_USEDEFAULT, 0, nullptr, nullptr, hInstance, nullptr);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow); 
   UpdateWindow(hWnd);

   return TRUE;
}

//
//  함수: WndProc(HWND, UINT, WPARAM, LPARAM)
//
//  용도: 주 창의 메시지를 처리합니다.
//
//  WM_COMMAND  - 애플리케이션 메뉴를 처리합니다.
//  WM_PAINT    - 주 창을 그립니다.
//  WM_DESTROY  - 종료 메시지를 게시하고 반환합니다.
//
//
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	RECT clientRectInfo;
    switch (message)
    {
    case WM_COMMAND:
        {
            int wmId = LOWORD(wParam);
            // 메뉴 선택을 구문 분석합니다:
            switch (wmId)
            {
            case IDM_ABOUT:
                DialogBox(hInst, MAKEINTRESOURCE(IDD_ABOUTBOX), hWnd, About);
                break;
            case IDM_EXIT:
                DestroyWindow(hWnd);
                break;
            case IDC_START_SENDER:
                // 쓰레드 생성
                hSenderThread = CreateThread(NULL, 0, RunSENDER, hWnd, 0, NULL);
                if (hSenderThread)
                {
                    CloseHandle(hSenderThread);  // 쓰레드 핸들 닫기
                }
                break;
            case IDC_STOP_SENDER:
                // Sender 종료
                stopSENDER();
                break;
            case IDC_START_RECEIVER:
                // 쓰레드 생성
                hReceiverThread = CreateThread(NULL, 0, RunRECEIVER, NULL, 0, NULL);
                if (hReceiverThread)
                {
                    CloseHandle(hReceiverThread);  // 쓰레드 핸들 닫기
                }
                break;
            case IDC_STOP_RECEIVER:
                // 쓰레드 생성
                stopRECEIVER();
                break;
            default:
                return DefWindowProc(hWnd, message, wParam, lParam);
            }
        }
        break;

    case WM_CREATE:
        OnCreate(hWnd, message, wParam, lParam);
        break;
    case WM_SIZE:
        OnSize(hWnd, message, wParam, lParam);
		clientRectInfo = getWinSize(hWnd);
        break;
    case WM_PAINT:
        {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hWnd, &ps);
            // TODO: 여기에 hdc를 사용하는 그리기 코드를 추가합니다...
            EndPaint(hWnd, &ps);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        FreeConsole();
        fclose(pCout);
        pCout = NULL;

        // MultimediaSender 객체 삭제
        mSender->stop();
        mSender->cleanup();
        delete mSender;

        // MultimediaReceiver 객체 삭제
        mReceiver->stop();
        mReceiver->cleanup();
        delete mReceiver;

        break;
    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}

// 정보 대화 상자의 메시지 처리기입니다.
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        break;
    }
    return (INT_PTR)FALSE;
}

typedef enum
{
	_BUTNUM_SEND_START,
	_BUTNUM_SEND_STOP,
	_BUTNUM_RECV_START,
	_BUTNUM_RECV_STOP,
	_BUTNUM_MAX
}E_BUT_NUM;

static LRESULT OnCreate(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	const unsigned int buttonWidth	= 120;
	const unsigned int buttonHeight	= 30;
	const unsigned int widthMargin	= 10;
	const unsigned int heightMargin	= 20;

    unsigned int posY[_BUTNUM_MAX] = {10,10,10,10};
    unsigned int posX[_BUTNUM_MAX] = {10,10,10,10};

	posX[_BUTNUM_SEND_STOP]		= posX[_BUTNUM_SEND_START] + buttonWidth + widthMargin;
	posX[_BUTNUM_RECV_START]	= posX[_BUTNUM_SEND_STOP] + buttonWidth + widthMargin;
	posX[_BUTNUM_RECV_STOP]		= posX[_BUTNUM_RECV_START] + buttonWidth + widthMargin;

    // 버튼 생성
    CreateWindow(
        _T("button"),
        _T("Start Sender"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_SEND_START], posY[_BUTNUM_SEND_START], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_START_SENDER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    // 버튼 생성
    CreateWindow(
        _T("button"),
        _T("Stop Sender"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_SEND_STOP], posY[_BUTNUM_SEND_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_SENDER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Start Receiver"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV_START], posY[_BUTNUM_RECV_START], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_START_RECEIVER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Stop Receiver"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV_STOP], posY[_BUTNUM_RECV_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_RECEIVER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    // 비디오 윈도우 생성
    videoWindow0 = CreateWindowW(
        L"STATIC",
        L"Video Window",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        600, 0, 320, 240,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow0, GWL_STYLE, GetWindowLongPtr(videoWindow0, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow0, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    // 비디오 윈도우 생성
    videoWindow1 = CreateWindowW(
        L"STATIC",
        L"Video Window",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        600, 300, 320, 240,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow1, GWL_STYLE, GetWindowLongPtr(videoWindow1, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow1, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    return 1;
}

LRESULT OnSize(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    int cxClient, cyClient;

    cxClient = LOWORD(lParam);
    cyClient = HIWORD(lParam);

    return DefWindowProc(hWnd, message, wParam, lParam);
}

RECT getWinSize(HWND hWnd)
{
	RECT rectSizeInfo;
	GetClientRect(hWnd, &rectSizeInfo);
	//printf("LRTB:%u,%u,%u,%u\n", rectSizeInfo.left, rectSizeInfo.right, rectSizeInfo.top, rectSizeInfo.bottom);
	return rectSizeInfo;
}

// 쓰레드 함수
DWORD WINAPI RunSENDER(LPVOID lpParam)
{
    // 쓰레드에서 실행할 로직을 작성합니다.
    // 예: 버튼 클릭 이벤트에 대한 처리 등
    //MessageBox(NULL, (LPCWSTR)"Thread is running!", (LPCWSTR)"Thread", MB_OK);
    //sender();
    HWND hWnd = reinterpret_cast<HWND>(lpParam);

    // Initialize sender pipelines
    if (!mSender->initialize())
    {
        std::cerr << "Failed to initialize sender pipelines." << std::endl;
        return 1;
    }

    // Set video resolution
	dynamic_cast<MultimediaSender*>(mSender)->setVideoResolution();


    // Set receiver IP and port
    dynamic_cast<MultimediaSender*>(mSender)->setReceiverIP();
    dynamic_cast<MultimediaSender*>(mSender)->setPort(5001,5002);

    // Set camera index (if necessary)
    dynamic_cast<MultimediaSender*>(mSender)->setCameraIndex(0);

    // Set video flip method (if necessary)
    dynamic_cast<MultimediaSender*>(mSender)->setVideoFlipMethod(4); // Horizontal flip

    // Set video encoding tune (if necessary)
	dynamic_cast<MultimediaSender*>(mSender)->setVideoEncTune(); 
	dynamic_cast<MultimediaSender*>(mSender)->setVideoEncBitRate();

    // Set audio encoding type (if necessary)
    dynamic_cast<MultimediaSender*>(mSender)->setAudioOpusencAudioType(2051); // Restricted low delay

    mSender->setWindow(videoWindow0);

    // Start sender pipelines
    mSender->start();

    WaitForSingleObject(hSenderThread, INFINITE);
    CloseHandle(hSenderThread);
    hSenderThread = INVALID_HANDLE_VALUE;
    return 0;
}

// 쓰레드 함수
DWORD WINAPI RunRECEIVER(LPVOID lpParam)
{
    // 쓰레드에서 실행할 로직을 작성합니다.
    // 예: 버튼 클릭 이벤트에 대한 처리 등
    //MessageBox(NULL, (LPCWSTR)"Thread is running!", (LPCWSTR)"Thread", MB_OK);
    //receiver();
    // Close Thread

    if (!mReceiver->initialize())
    {
        std::cerr << "Failed to initialize MultimediaReceiver." << std::endl;
        return -1;
    }
    mReceiver->setPort(5001, 5002);

    dynamic_cast<MultimediaReceiver*>(mReceiver)->setJitterBuffer(200);

    dynamic_cast<MultimediaReceiver*>(mReceiver)->setRTP();

    mReceiver->setWindow(videoWindow1);

    mReceiver->start();

    WaitForSingleObject(hReceiverThread, INFINITE);
    CloseHandle(hReceiverThread);
    hReceiverThread = INVALID_HANDLE_VALUE;
    return 0;
}

static void SetStdOutToNewConsole(void)
{
    // Allocate a console for this app
    AllocConsole();
    //AttachConsole(ATTACH_PARENT_PROCESS);
    freopen_s(&pCout, "CONOUT$", "w", stdout);
}

static void stopSENDER() {
    // Stop sender pipelines
    mSender->stop();
}

static void stopRECEIVER() {
    // Stop sender pipelines
    mReceiver->stop();
}


