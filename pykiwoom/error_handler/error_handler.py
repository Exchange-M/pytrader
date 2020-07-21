from abc import *
from functools import wraps

from PyQt5.QtWidgets import QMessageBox


def critical_error_decorator(error_class):
    @wraps(error_class)
    def handling_error(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_class as e:
                show_dialog('Critical', e)
                raise error_class()
        return func_wrapper
    return handling_error


def show_dialog(grade, err_cls):
    grade_table = {'Information': 1, 'Warning': 2, 'Critical': 3, 'Question': 4}
    dialog = QMessageBox()
    dialog.setIcon(grade_table[grade])
    dialog.setText(err_cls.detail())
    dialog.setWindowTitle(grade)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()


class AbstractError(metaclass=ABCMeta):
    @abstractmethod
    def detail(self):
        pass


class CancelOrderError(AbstractError, Exception):
    def __init__(self, msg="주문 취소 입력값이 잘못되었습니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class AutomatedOrderError(AbstractError, Exception):
    def __init__(self, msg="자동 주문 오류입니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class ManualOrderError(AbstractError, Exception):
    def __init__(self, msg="수동 주문 입력값이 잘못되었습니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class ParameterTypeError(AbstractError, Exception):
    """ 파라미터 타입이 일치하지 않을 경우 발생하는 예외 """

    def __init__(self, msg="파라미터 타입이 일치하지 않습니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class NotHoldingOrderError(AbstractError, Exception):
    """ 매도할 종목을 보유하지 않은 경우 발생하는 예외 """

    def __init__(self, msg="매도 종목을 보유하고 있지 않습니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class ParameterValueError(AbstractError, Exception):
    """ 파라미터로 사용할 수 없는 값을 사용할 경우 발생하는 예외 """

    def __init__(self, msg="파라미터로 사용할 수 없는 값 입니다."):
        self.msg = msg

    def detail(self):
        return self.msg


class KiwoomProcessingError(AbstractError, Exception):
    """ 키움에서 처리실패에 관련된 리턴코드를 받았을 경우 발생하는 예외 """

    def __init__(self, msg="키움 서버 처리 실패"):
        self.msg = msg

    def detail(self):
        return self.msg


class KiwoomConnectError(AbstractError, Exception):
    """ 키움서버에 로그인 상태가 아닐 경우 발생하는 예외 """

    def __init__(self, msg="로그인 여부를 확인하십시오"):
        self.msg = msg

    def detail(self):
        return self.msg
