// WindowsApp.cpp : 애플리케이션에 대한 진입점을 정의합니다.
//

#include "framework.h"
#include "WindowsApp.h"
#include <Commctrl.h>
#include <Windows.h>
#include <gst/gst.h>
#include <stdio.h>

//#include "MultimediaSender.h"
#include "MultimediaReceiver.h"
#include "MultimediaInterface.h"
#include "MultimediaManager.h"
#include "global_setting.h"

#define MAX_LOADSTRING 100

// functions
LRESULT OnSize(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
RECT getWinSize(HWND hWnd);
static LRESULT OnCreate(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);

DWORD WINAPI RunRECEIVER(LPVOID lpParam);
DWORD WINAPI RunRECEIVER2(LPVOID lpParam);
DWORD WINAPI RunRECEIVER3(LPVOID lpParam);
static void SetStdOutToNewConsole(void);


static void stopRECEIVER();
static void stopRECEIVER2();
static void stopRECEIVER3();

// 전역 변수:
HINSTANCE hInst;                                // 현재 인스턴스입니다.
WCHAR szTitle[MAX_LOADSTRING];                  // 제목 표시줄 텍스트입니다.
WCHAR szWindowClass[MAX_LOADSTRING];            // 기본 창 클래스 이름입니다.

static FILE* pCout = NULL;

HWND hWndMain;

HANDLE hSenderThread;
HANDLE hReceiverThread;
HANDLE hReceiver2Thread;
HANDLE hReceiver3Thread;

MultimediaManager& mManager = MultimediaManager::GetInstance();
//MultimediaInterface* mReceiver = new MultimediaReceiver();
//MultimediaInterface* mReceiver2 = new MultimediaReceiver();
//MultimediaInterface* mReceiver3 = new MultimediaReceiver();

HWND videoWindow0; // Video 출력용 윈도우 핸들
HWND videoWindow1; // Video 출력용 윈도우 핸들
HWND videoWindow2; // Video 출력용 윈도우 핸들
HWND videoWindow3; // Video 출력용 윈도우 핸들

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

   HWND hWnd = CreateWindowEx(
       0,
       szWindowClass,  // 클래스 이름
       szTitle,        // 윈도우 타이틀
       WS_OVERLAPPEDWINDOW,  // 윈도우 스타일
       CW_USEDEFAULT,  // x좌표
       CW_USEDEFAULT,  // y좌표
       1000,            // width
       700,            // height
       nullptr,
       nullptr,
       hInstance,
       nullptr
   );

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
                mManager.setupSender(videoWindow0, "127.0.0.1", 10001, 10002); // init manager with my video view
                // Server Ip has been set up at initialize
                mManager.makeCall(); // Receiver is decided by server application, just send video and audio
                break;
            case IDC_STOP_SENDER:
                mManager.pauseCall();
                break;
            case IDC_START_RECEIVER:
                mManager.setupReceiver(videoWindow1, 10001, 10002, 1); // first video setup
                mManager.playReceiver(1);
                break;
            case IDC_STOP_RECEIVER:
                mManager.pauseReceiver(1);
                break;
            case IDC_START_RECEIVER2:
                mManager.setupReceiver(videoWindow2, 10001, 10002, 2); // first video setup
                mManager.playReceiver(2);
                break;
            case IDC_STOP_RECEIVER2:
                mManager.pauseReceiver(2);
                break;
            case IDC_START_RECEIVER3:
                mManager.setupReceiver(videoWindow3, 10001, 10002, 3); // first video setup
                mManager.playReceiver(3);
                break;
            case IDC_STOP_RECEIVER3:
                mManager.pauseReceiver(3);
                break;
            case IDC_ACCEPT_ALL:
                mManager.setupReceiver(videoWindow1, 10001, 10002, 1); // first video setup
                mManager.setupReceiver(videoWindow2, 10001, 10002, 2); // second video setup
                mManager.setupReceiver(videoWindow3, 10001, 10002, 3); // third video setup
                mManager.playReceiver(1);
                mManager.playReceiver(2);
                mManager.playReceiver(3);
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

        // MultimediaReceiver 객체 삭제
        //mReceiver->stop();
        //mReceiver->cleanup();
        //delete mReceiver;

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
	_BUTNUM_RECV1_START,
	_BUTNUM_RECV1_STOP,
    _BUTNUM_RECV2_START,
    _BUTNUM_RECV2_STOP,
    _BUTNUM_RECV3_START,
    _BUTNUM_RECV3_STOP,
    _BUTNUM_RECV_ACCEPT_ALL,
	_BUTNUM_MAX
}E_BUT_NUM;

typedef enum
{
    _VIDEO_0,
    _VIDEO_1,
    _VIDEO_2,
    _VIDEO_3,
    _VIDEO_VIEW_MAX
}E_VIDEO_NUM;

static LRESULT OnCreate(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    const unsigned int videoWidth = 320;
    const unsigned int videoHeight = 240;
    const unsigned int videoWidthMargin = 20;
    const unsigned int videoHeightMargin = 80;

    unsigned int videoPosX[_VIDEO_VIEW_MAX] = { 20, };
    unsigned int videoPosY[_VIDEO_VIEW_MAX] = { 20, };

    videoPosX[_VIDEO_1] = videoPosX[_VIDEO_0] + videoWidth + videoWidthMargin;
    videoPosY[_VIDEO_1] = videoPosY[_VIDEO_0];


    videoPosX[_VIDEO_2] = videoPosX[_VIDEO_0];
    videoPosY[_VIDEO_2] = videoPosY[_VIDEO_0] + videoHeight + videoHeightMargin;


    videoPosX[_VIDEO_3] = videoPosX[_VIDEO_1];
    videoPosY[_VIDEO_3] = videoPosY[_VIDEO_2];


    // 비디오 윈도우 생성
    videoWindow0 = CreateWindowW(
        L"STATIC",
        L"Video Window",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        videoPosX[_VIDEO_0], videoPosY[_VIDEO_0], videoWidth, videoHeight,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow0, GWL_STYLE, GetWindowLongPtr(videoWindow0, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow0, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    // 비디오 윈도우 생성
    videoWindow1 = CreateWindowW(
        L"STATIC",
        L"Video Window1",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        videoPosX[_VIDEO_1], videoPosY[_VIDEO_1], videoWidth, videoHeight,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow1, GWL_STYLE, GetWindowLongPtr(videoWindow1, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow1, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    // 비디오 윈도우 생성
    videoWindow2 = CreateWindowW(
        L"STATIC",
        L"Video Window2",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        videoPosX[_VIDEO_2], videoPosY[_VIDEO_2], videoWidth, videoHeight,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow2, GWL_STYLE, GetWindowLongPtr(videoWindow2, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow2, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    // 비디오 윈도우 생성
    videoWindow3 = CreateWindowW(
        L"STATIC",
        L"Video Window3",
        WS_CHILD | WS_VISIBLE | WS_BORDER,
        videoPosX[_VIDEO_3], videoPosY[_VIDEO_3], videoWidth, videoHeight,
        hWnd, nullptr, hInst, nullptr
    );
    // 비디오 출력을 위해 윈도우 스타일을 설정합니다.
    SetWindowLongPtr(videoWindow3, GWL_STYLE, GetWindowLongPtr(videoWindow3, GWL_STYLE) | WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
    SetWindowPos(videoWindow3, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_ASYNCWINDOWPOS);

    const unsigned int buttonWidth = 100;
    const unsigned int buttonHeight = 30;
    const unsigned int widthMargin = 20;
    const unsigned int heightMargin = 20;

    unsigned int posX[_BUTNUM_MAX] = { 70, };
    unsigned int posY[_BUTNUM_MAX] = { 270, };

    posX[_BUTNUM_SEND_START] = videoPosX[_VIDEO_0] + (videoWidth / 4) - (buttonWidth / 3);
    posY[_BUTNUM_SEND_START] = videoPosY[_VIDEO_0] + videoHeight + 10;
    posX[_BUTNUM_SEND_STOP] = posX[_BUTNUM_SEND_START] + buttonWidth + widthMargin;
    posY[_BUTNUM_SEND_STOP] = posY[_BUTNUM_SEND_START];

    posX[_BUTNUM_RECV1_START] = videoPosX[_VIDEO_1] + (videoWidth / 4) - (buttonWidth / 3);
    posY[_BUTNUM_RECV1_START] = videoPosY[_VIDEO_1] + videoHeight + 10;
    posX[_BUTNUM_RECV1_STOP] = posX[_BUTNUM_RECV1_START] + buttonWidth + widthMargin;
    posY[_BUTNUM_RECV1_STOP] = posY[_BUTNUM_RECV1_START];

    posX[_BUTNUM_RECV2_START] = videoPosX[_VIDEO_2] + (videoWidth / 4) - (buttonWidth / 3);
    posY[_BUTNUM_RECV2_START] = videoPosY[_VIDEO_2] + videoHeight + 10;
    posX[_BUTNUM_RECV2_STOP] = posX[_BUTNUM_RECV2_START] + buttonWidth + widthMargin;
    posY[_BUTNUM_RECV2_STOP] = posY[_BUTNUM_RECV2_START];

    posX[_BUTNUM_RECV3_START] = videoPosX[_VIDEO_3] + (videoWidth / 4) - (buttonWidth / 3);
    posY[_BUTNUM_RECV3_START] = videoPosY[_VIDEO_3] + videoHeight + 10;
    posX[_BUTNUM_RECV3_STOP] = posX[_BUTNUM_RECV3_START] + buttonWidth + widthMargin;
    posY[_BUTNUM_RECV3_STOP] = posY[_BUTNUM_RECV3_START];

    posX[_BUTNUM_RECV_ACCEPT_ALL] = 700;
    posY[_BUTNUM_RECV_ACCEPT_ALL] = 10;


    // 버튼 생성
    CreateWindow(
        _T("button"),
        _T("Start"),
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
        _T("Stop"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_SEND_STOP], posY[_BUTNUM_SEND_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_SENDER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Start R1"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV1_START], posY[_BUTNUM_RECV1_START], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_START_RECEIVER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Stop R1"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV1_STOP], posY[_BUTNUM_RECV1_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_RECEIVER,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Start R2"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV2_START], posY[_BUTNUM_RECV2_START], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_START_RECEIVER2,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Stop R2"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV2_STOP], posY[_BUTNUM_RECV2_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_RECEIVER2,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Start R3"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV3_START], posY[_BUTNUM_RECV3_START], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_START_RECEIVER3,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("Stop R3"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV3_STOP], posY[_BUTNUM_RECV3_STOP], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_STOP_RECEIVER3,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

    CreateWindow(
        _T("button"),
        _T("AcceptAll"),
        WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        posX[_BUTNUM_RECV_ACCEPT_ALL], posY[_BUTNUM_RECV_ACCEPT_ALL], buttonWidth, buttonHeight,
        hWnd,
        (HMENU)IDC_ACCEPT_ALL,
        ((LPCREATESTRUCT)lParam)->hInstance,
        NULL
    );

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

static void SetStdOutToNewConsole(void)
{
    // Allocate a console for this app
    AllocConsole();
    //AttachConsole(ATTACH_PARENT_PROCESS);
    freopen_s(&pCout, "CONOUT$", "w", stdout);
}
