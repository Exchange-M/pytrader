import time
from abc import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

from utils import json2sell_buy, clean_duplicate_2d


class AbstractDisplay(metaclass=ABCMeta):
    def __init__(self, parent):
        self.parent = parent

    @abstractmethod
    def __call__(self):
        pass

    def check_account_filled(self):
        if self.parent.accountComboBox.currentText():
            return True


class ManualOrderDisplay(AbstractDisplay):
    def __call__(self):
        self.__display_account_table()

    def __request_account_info(self):
        account_list = self.parent.kiwoom.get_login_info("ACCNO").split(';')
        return account_list

    def __display_account_table(self):
        cnt = int(self.parent.kiwoom.get_login_info("ACCOUNT_CNT"))
        account_list = self.__request_account_info()
        self.parent.accountComboBox.addItems(account_list[0:cnt])


class LogDisplay(AbstractDisplay):
    def __call__(self):
        if self.parent.kiwoom.msg:
            self.parent.logTextEdit.append(self.parent.kiwoom.msg)
            self.parent.kiwoom.msg = ""


class AutomaticOrderListDisplay(AbstractDisplay):
    def __call__(self):
        self.__display_automated_stocks_table()

    def __make_automated_stock_table(self, order, order_type):
        cnt = len(order)
        exec(f"self.parent.automated{order_type}StocksTable.setRowCount({cnt})")

        for row, v in enumerate(order.values()):
            del v['code']
            for col, n in enumerate(v):
                item = QTableWidgetItem(v[n])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                exec(f'self.parent.automated{order_type}StocksTable.setItem(row, col, item)')
        exec(f"self.parent.automated{order_type}StocksTable.resizeRowsToContents()")

    def __display_automated_stocks_table(self):
        file_list = ["Sell.json", "Buy.json"]
        sell_buy_dict = json2sell_buy(file_list)
        for order_type, order in sell_buy_dict.items():
            self.__make_automated_stock_table(order, order_type)


class DepositAndHoldingStocksDisplay(AbstractDisplay):
    def __call__(self):
        if self.check_account_filled():
            self.__request_deposit()
            self.__request_account_evaluation()

            self.__display_deposit_evaluation_table()
            self.__display_holding_stock_table()

    def __display_deposit_evaluation_table(self):
        item = QTableWidgetItem(self.parent.kiwoom.data_opw00001)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.parent.accountEvaluationTable.setItem(0, 0, item)
        length = len(self.parent.kiwoom.data_opw00018['account_evaluation'])
        for i in range(1, length + 1):
            item = QTableWidgetItem(self.parent.kiwoom.data_opw00018['account_evaluation'][i - 1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.parent.accountEvaluationTable.setItem(0, i, item)
        self.parent.accountEvaluationTable.resizeRowsToContents()

    def __display_holding_stock_table(self):
        stocks = clean_duplicate_2d(self.parent.kiwoom.data_opw00018['stocks'])
        self.parent.stocksTable.setRowCount(len(stocks))
        for row in range(len(stocks)):
            for col in range(len(stocks[row]) - 1):
                item = QTableWidgetItem(stocks[row][col])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.parent.stocksTable.setItem(row, col, item)
        self.parent.stocksTable.resizeRowsToContents()

    def __request_deposit(self):
        self.parent.kiwoom.set_input_value("계좌번호", self.parent.accountComboBox.currentText())
        self.parent.kiwoom.comm_rq_data("예수금상세현황요청", "opw00001", 0, "2000")

    def __request_account_evaluation(self):
        self.parent.kiwoom.set_input_value("계좌번호", self.parent.accountComboBox.currentText())
        self.parent.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "2000")
        while self.parent.kiwoom.inquiry == '2':
            time.sleep(0.2)
            self.parent.kiwoom.set_input_value("계좌번호", self.parent.accountComboBox.currentText())
            self.parent.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 2, "2")


class NotConcludedOrderDisplay(AbstractDisplay):
    def __call__(self):
        if self.check_account_filled():
            self.__request_not_concluded_stock()
            self.__display_not_concluded_stocks_table()

    def __display_not_concluded_stocks_table(self):
        not_concluded_stocks = self.parent.kiwoom.opt10075

        self.parent.notConcludedOrderTable.setRowCount(len(not_concluded_stocks))
        for row, v in enumerate(not_concluded_stocks):
            for col, _ in enumerate(v):
                item = QTableWidgetItem(v[col])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.parent.notConcludedOrderTable.setItem(row, col, item)
        self.parent.notConcludedOrderTable.resizeRowsToContents()

    def __request_not_concluded_stock(self):
        self.parent.kiwoom.set_input_value("계좌번호", self.parent.accountComboBox.currentText())
        self.parent.kiwoom.set_input_value("체결구분", "1")  # 2는 체결 0은 전체
        self.parent.kiwoom.set_input_value("매매구분", "0")
        self.parent.kiwoom.comm_rq_data("실시간미체결요청", "opt10075", 0, "1000")
