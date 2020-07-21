from abc import *

from PyQt5.QtCore import QTimer, QTime


class AbstractTimer(metaclass=ABCMeta):
    def __init__(self, parent, sec):
        self.parent = parent
        self.sec = sec
        self.timer = QTimer(self.parent)
        self.timer.start(1000 * self.sec)
        self.timer.timeout.connect(self.parent.timeout)

    @abstractmethod
    def timeout(self):
        pass


class MainTimer(AbstractTimer):
    def timeout(self):
        if self.parent.kiwoom.get_connect_state() == 1:
            state = self.parent.server_gubun + " 서버 연결중"
        else:
            state = "서버 미연결"

        if self.parent.kiwoom.refresh:
            self.parent.refresh_all()

        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.parent.statusbar.showMessage("현재시간: " + current_time + " | " + state)
        self.parent.display_log()


class AutomaticOrderTimer(AbstractTimer):
    def timeout(self):
        automatic_order_time = QTime.currentTime().toString("hhmm")
        # 자동 주문 실행
        # 1100은 11시 00분을 의미합니다.
        print("current time: %d" % int(automatic_order_time))
        if self.parent.is_automatic_order and 930 <= int(automatic_order_time) <= 1530:
            self.parent.AutomaticOrder.send_order()


class RefreshTimer(AbstractTimer):
    def timeout(self):
        if self.parent.realtimeCheckBox.isChecked():
            self.parent.refresh_all()
