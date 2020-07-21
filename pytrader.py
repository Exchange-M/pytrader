import qdarkstyle
from PyQt5 import uic
from PyQt5.QtGui import QIntValidator
from pykiwoom.display import ManualOrderDisplay, LogDisplay, \
    AutomaticOrderListDisplay, DepositAndHoldingStocksDisplay, NotConcludedOrderDisplay
from pykiwoom.order import ManualOrder, AutomaticOrder, CancelOrder
from pykiwoom.timer import MainTimer, AutomaticOrderTimer, RefreshTimer

from pykiwoom.kiwoom import *
from pykiwoom.wrapper import *
from utils import *

form_class = uic.loadUiType("pytrader.ui")[0]
KOSPI_CODE = 0
KODAQ_CODE = 10
MAINTIMER_SEC = 1
AUTOMATICORERTIMER_SEC = 20
REFRESHTIMER_SEC = 30


class MyWindow(QMainWindow, form_class):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        if self.kiwoom.get_login_info("GetServerGubun"):
            self.server_gubun = "실제운영"
        else:
            self.server_gubun = "모의투자"

        self.orderBtn.clicked.connect(self.send_manual_order)
        self.inquiryBtn.clicked.connect(self.refresh_all)
        self.codeLineEdit.setValidator(QIntValidator())
        self.codeLineEdit.textChanged.connect(self.autocomplete_name_by_code)
        self.stocksTable.cellClicked.connect(self.autocomplete_order_fields)
        self.notConcludedOrderTable.cellClicked.connect(self.autocomplete_cancel_fields)
        self.orderCancelBtn.clicked.connect(self.send_cancel_order)

        self.file_list = ["Sell.json", "Buy.json"]
        self.detail_account_info_event_loop = QEventLoop()
        self.is_automatic_order = False
        self.in_processing = False
        self.cancel_dict = {}

        self.MainTimer = MainTimer(self, MAINTIMER_SEC)
        self.AutomaticOrderTimer = AutomaticOrderTimer(self, AUTOMATICORERTIMER_SEC)
        self.RefreshTimer = RefreshTimer(self, REFRESHTIMER_SEC)

        self.ManualOrderDisplay = ManualOrderDisplay(self)
        self.AutomaticOrderListDisplay = AutomaticOrderListDisplay(self)
        self.DepositAndHoldingStocksDisplay = DepositAndHoldingStocksDisplay(self)
        self.NotConcludedOrderDisplay = NotConcludedOrderDisplay(self)
        self.LogDisplay = LogDisplay(self)

        self.AutomaticOrder = AutomaticOrder(self)
        self.ManualOrder = ManualOrder(self)
        self.CancelOrder = CancelOrder(self)

        self.refresh_all()

    def display_manual_order(self):
        self.ManualOrderDisplay()

    def display_automatic_order_list(self):
        self.AutomaticOrderListDisplay()

    def display_deposit_and_holding_stocks(self):
        self.DepositAndHoldingStocksDisplay()

    def display_not_concluded_stocks(self):
        self.NotConcludedOrderDisplay()

    def display_log(self):
        self.LogDisplay()

    def send_manual_order(self):
        self.in_processing = True
        self.ManualOrder.send_order()
        self.in_processing = False

    def send_automatic_order(self):
        self.in_processing = True
        self.AutomaticOrder.send_order()
        self.in_processing = False

    def send_cancel_order(self):
        self.in_processing = True
        self.CancelOrder.send_order()
        self.in_processing = False

    def refresh_all(self):
        self.in_processing = True

        self.display_manual_order()
        self.display_automatic_order_list()
        self.display_deposit_and_holding_stocks()
        self.display_not_concluded_stocks()
        self.display_log()

        self.write_stocks_in_account()
        self.kiwoom.opw_data_reset()
        self.kiwoom.refresh = False
        self.in_processing = False

    def timeout(self):
        sender = self.sender()
        if self.in_processing:
            return

        if id_equal(sender, self.MainTimer.timer):
            self.MainTimer.timeout()
        elif id_equal(sender, self.AutomaticOrderTimer.timer):
            self.AutomaticOrderTimer.timeout()
        elif id_equal(sender, self.RefreshTimer.timer):
            self.RefreshTimer.timeout()

    def autocomplete_name_by_code(self):
        code = self.codeLineEdit.text()
        code_list = self.kiwoom.get_code_list(KOSPI_CODE, KODAQ_CODE)

        if empty_check(code):
            self.codeNameLineEdit.setText('')
            return

        if code in code_list:
            code_name = self.kiwoom.get_master_code_name(code)
            self.codeNameLineEdit.setText(code_name)

    def autocomplete_cancel_fields(self):
        if empty_check(table_row2dict(self.notConcludedOrderTable)):
            return
        else:
            self.cancel_dict = table_row2dict(self.notConcludedOrderTable)

    def autocomplete_order_fields(self):
        if empty_check(table_row2dict(self.stocksTable)):
            return
        else:
            row = table_row2dict(self.stocksTable)

        self.codeLineEdit.setText(extract_digits_from_string(row["종목 번호"]))
        self.qtySpinBox.setValue(int(row["보유량"]))
        self.priceSpinBox.setValue(int(clean_price_value(row["현재가"])))
        self.orderTypeComboBox.setCurrentText("신규매도")

    def write_stocks_in_account(self):
        NAME_FLAG = 0
        stocks_in_account = {}
        stocks = clean_duplicate_2d(self.kiwoom.data_opw00018['stocks'])
        keys = get_table_header(self.stocksTable)

        stocks_in_account['deposit'] = clean_price_value(self.kiwoom.data_opw00001)

        for stock in stocks:
            name = stock[NAME_FLAG]
            stocks_in_account[name] = dict(zip(keys, stock))

        write_json('./data/stocks_in_account.json', stocks_in_account)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
