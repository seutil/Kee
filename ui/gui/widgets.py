
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ExpirationDateWidget(QFrame):

    def __init__(self, *args, text: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.__initializeUI()
        self.__initializeConnections()
        self.setText(text)

    def __initializeUI(self) -> None:
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.__lbl_delimiter = QLabel('/')
        self.__combo_month = QComboBox()
        self.__combo_year = QComboBox()

        self.__combo_month.addItems(['—'] + [str(i).zfill(2) for i in range(1, 13)])
        self.__combo_year.addItems(['—'] + [str(i).zfill(2) for i in range(0, 100)])

        self.__combo_month.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.__lbl_delimiter.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.__combo_year.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        lyt_main = QHBoxLayout()
        lyt_main.addWidget(self.__combo_month)
        lyt_main.addWidget(self.__lbl_delimiter)
        lyt_main.addWidget(self.__combo_year)
        self.setLayout(lyt_main)

    def __initializeConnections(self) -> None:
        self.__combo_month.currentIndexChanged.connect(self.__currentIndexChanged)
        self.__combo_year.currentIndexChanged.connect(self.__currentIndexChanged)

    def __currentIndexChanged(self, index: int) -> None:
        if index == 0:
            self.__combo_month.setCurrentIndex(0)
            self.__combo_year.setCurrentIndex(0)
        elif self.sender() is self.__combo_month:
            self.__combo_year.setCurrentIndex(self.__combo_year.currentIndex() or 1)
        elif self.sender() is self.__combo_year:
            self.__combo_month.setCurrentIndex(self.__combo_month.currentIndex() or 1)

    def text(self) -> str:
        month = self.__combo_month.currentText()
        year = self.__combo_year.currentText()
        if month == "—" or year == "—":
            return ""

        return f'{month}/{year}'

    def setText(self, date: str) -> None:
        if not date:
            self.__combo_month.setCurrentIndex(0)
            self.__combo_year.setCurrentIndex(0)
            return

        month, year = date.split('/')
        self.__combo_month.setCurrentIndex(self.__combo_month.findText(month))
        self.__combo_year.setCurrentIndex(self.__combo_year.findText(year))
