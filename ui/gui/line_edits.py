
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SelectFileLineEdit(QLineEdit):

    def __init__(self, dialog: QFileDialog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog = dialog
        self._act_select_file = QAction(QIcon(":/icons/dots"), "", self, triggered=self.dialog.exec_)
        self.addAction(self._act_select_file, QLineEdit.TrailingPosition)
        self.dialog.fileSelected.connect(lambda file: self.setText(file))


class PasswordLineEdit(QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__act_change_echo_mode = QAction('', self)
        self.addAction(self.__act_change_echo_mode, QLineEdit.TrailingPosition)
        self.setEchoMode(QLineEdit.Password)
        self.__act_change_echo_mode.triggered.connect(self._changeEchoMode)

    def setEchoMode(self, echo_mode: 'QLineEdit.EchoMode') -> None:
        icon = QIcon(f':/icons/{"hide" if echo_mode == QLineEdit.Normal else "show"}-password')
        self.__act_change_echo_mode.setIcon(icon)
        super().setEchoMode(echo_mode)

    def _changeEchoMode(self) -> None:
        echo_mode = self.echoMode()
        self.setEchoMode(QLineEdit.Password if echo_mode == QLineEdit.Normal else QLineEdit.Normal)
