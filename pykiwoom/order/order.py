from abc import *

from pykiwoom.error_handler import AutomatedOrderError, ManualOrderError, critical_error_decorator, show_dialog, \
    NotHoldingOrderError, CancelOrderError

from utils import json2sell_buy


class AbstractOrder(metaclass=ABCMeta):
    def __init__(self, parent):
        self.parent = parent

        self.order_type_table = {'': -1, '신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        self.bid_type_table = {'지정가': "00", '시장가': "03"}
        self.file_list = ["Sell.json", "Buy.json"]
        self.account = self.parent.accountComboBox.currentText()
        self.order_type = ''
        self.code = ''
        self.name = ''
        self.bid_type = ''
        self.qty = ''
        self.price = ''
        self.order_no = ''

    @abstractmethod
    def send_order(self):
        pass

    def request_order(self, request_name):
        self.parent.kiwoom.send_order(request_name, "0101", self.account, int(self.order_type), self.code,
                                      int(self.qty), int(self.price), self.bid_type, self.order_no)

        if self.__check_order_completed():
            print("order_no: ", self.parent.kiwoom.order_no)
            print(f"[{self.name}] {request_name} 주문이 접수되었습니다.")
            self.__reset_order_no()
        else:
            print(f"[{self.name}] {request_name} 주문이 접수되지 않았습니다.")
            print(AutomatedOrderError())
            # 자동 주문 작업 완료 후, 출력이 아닌 경고창으로 대체

    def __reset_order_no(self):
        self.parent.kiwoom.order_no = ""

    def __check_order_completed(self):
        if self.parent.kiwoom.order_no:
            return True
        else:
            return False


class ManualOrder(AbstractOrder):
    @critical_error_decorator(ManualOrderError)
    def send_order(self):
        if self.__check_manual_order_error():
            self.__set_up_order_info()
            self.request_order("수동주문")
        else:
            show_dialog('Warning', ManualOrderError())
            return

    def __check_manual_order_error(self):
        if (not self.parent.codeLineEdit.text() or
            not self.parent.accountComboBox.currentText() or
                not self.parent.orderTypeComboBox.currentText()):
            return False
        else:
            return True

    def __set_up_order_info(self):
        self.order_type = self.order_type_table[self.parent.orderTypeComboBox.currentText()]
        self.code = self.parent.codeLineEdit.text()
        self.name = self.parent.kiwoom.get_master_code_name(self.code)
        self.bid_type = self.bid_type_table[self.parent.bidTypeComboBox.currentText()]
        self.qty = self.parent.qtySpinBox.value()
        self.price = self.parent.priceSpinBox.value()
        self.account = self.parent.accountComboBox.currentText()
        self.order_no = ''


class AutomaticOrder(AbstractOrder):
    @critical_error_decorator(AutomatedOrderError)
    def send_order(self):
        sell_buy = json2sell_buy(self.file_list)
        self.__sell_order(sell_buy['Sell'])
        self.__buy_order(sell_buy['Buy'])

    def __check_holding_stocks(self):
        NAME_FLAG = 0
        holding_stocks_name = [stock[NAME_FLAG] for stock in self.parent.kiwoom.data_opw00018['stocks']]
        if self.name not in holding_stocks_name:
            print(f"[{self.name}] 자동매도주문이 접수되지 않았습니다.")
            print(NotHoldingOrderError())
            return False
        else:
            return True

    def __set_up_order_info(self, order_dict, order_flag):
        self.order_type = order_flag
        self.code = order_dict['code']
        self.name = order_dict['name']
        self.bid_type = self.bid_type_table[order_dict['bid_type']]
        self.qty = order_dict['quantity']
        self.price = order_dict['price']
        self.account = self.parent.accountComboBox.currentText()
        self.order_no = ''

    def __sell_order(self, orders):
        SELL_FLAG = 2
        for order in orders.values():
            self.__set_up_order_info(order, SELL_FLAG)
            if self.__check_holding_stocks():
                self.request_order("자동매도주문")

    def __buy_order(self, orders):
        BUY_FLAG = 1
        for order in orders.values():
            self.__set_up_order_info(order, BUY_FLAG)
            self.request_order("자동매수주문")


class CancelOrder(AbstractOrder):
    def send_order(self):
        if self.__check_cancel_dict():
            self.__set_up_order_info()
            self.request_order("주문취소")
        else:
            show_dialog('Warning', CancelOrderError())
            return

    def __check_cancel_dict(self):
        if self.parent.cancel_dict:
            return True

    def __set_up_order_info(self):
        set_bid_type = "00"
        self.account = self.parent.accountComboBox.currentText()
        self.order_type = self.order_type_table[
            self.__extract_order_type(self.parent.cancel_dict['구분'])
        ]
        self.name = self.parent.cancel_dict['종목명']
        self.qty = self.parent.cancel_dict['수량']
        self.price = self.parent.cancel_dict['주문가']
        self.order_no = self.parent.cancel_dict['주문번호']
        self.code = self.parent.cancel_dict['종목코드']
        self.bid_type = set_bid_type

    @staticmethod
    def __extract_order_type(order_type):
        extract_sign = 1
        return order_type[extract_sign:] + '취소'
