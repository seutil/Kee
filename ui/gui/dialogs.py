
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


DATABASE_FILE_EXTENSION = "kdb"


class SaveDatabaseDialog(QFileDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Save Database...")
        self.setFileMode(QFileDialog.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setNameFilters([
            f"Kee Database (*.{DATABASE_FILE_EXTENSION})",
            "All Files (*.*)",
        ])

    def location(self) -> str | None:
        if self.selectedFiles() is None:
            return None

        self.selectedFiles()[0]

    def fileName(self) -> str | None:
        if self.location is None:
            return None

        return os.path.basename(self.location).split('.')[0]


class OpenDatabaseDialog(QFileDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Open Database...")
        self.setFileMode(QFileDialog.ExistingFile)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setNameFilters([
            f"Kee Database (*.{DATABASE_FILE_EXTENSION})",
            "All Files (*.*)"
        ])

    def location(self) -> str:
        self.selectedFiles()[0]
