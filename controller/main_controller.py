from model.conferenceroom import ConferenceRoom
from model.conferencecall_broker import conferencecallbroker
from utils.call_state import CallState


class MainController:
    def __init__(self, main_window, main_view, account_view):
        self.main_window = main_window
        self.main_view = main_view
        self.account_view = account_view

    def main_button_clicked(self):
        self.main_window.stacked_widget.setCurrentWidget(self.account_view)

    def conference_button_clicked(self):
        # conference room 을 생성
        conf_room = ConferenceRoom(4);
        print(f'로그인한 총 {conf_room.get_participants_number()}명(MAX:{conf_room.number_of_participants}명)에게 초청메시지 전송')
        conf_room.set_room_id(str(conferencecallbroker.make_room_id())) # room 번호 생성
        conf_room.set_state(CallState.JOIN)
        # directory service 에 있는 user 들에게 모두 JOIN 메시지를 발송한다.
        conferencecallbroker.append(conf_room)
        pass
