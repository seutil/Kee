
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib.core.database import Status, DatabaseInterface
from lib.core.data.group import GroupInterface, Type


class _DatabaseStandardItem(QStandardItem):

    def __init__(self, database: DatabaseInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database = database
        self._loaded = 0

    def data(self, role: Qt.ItemDataRole) -> QVariant:
        if role == Qt.DisplayRole:
            self._updateChilds()
            return self._database.name() + (" *" if self._database.status() == Status.MODIFIED else "")

        if role == Qt.DecorationRole:
            closed = self._database.status() == Status.CLOSED
            icon = QIcon(":/icons/lock" if closed else ":/icons/unlock")
            return icon

        if role == Qt.EditRole:
            return self._database.name()

        return QVariant()

    def setData(self, value: QVariant, role: Qt.ItemDataRole) -> None:
        if role != Qt.EditRole:
            return

        self._database.name(value)

    def flags(self) -> Qt.ItemFlags:
        if self._database.status() == Status.CLOSED:
            return super().flags() & ~Qt.ItemIsEditable

        return super().flags() | Qt.ItemIsEditable

    def _updateChilds(self) -> None:
        if self._database.status() != Status.CLOSED:
            if self._loaded == len(self._database.groups()):
                return

            for group in self._database.groups()[self._loaded:]:
                self.appendRow(_GroupStandardItem(group))

            self._loaded = len(self._database.groups())

        if self._database.status() == Status.CLOSED and self.hasChildren():
            self.removeRows(0, self.rowCount())


class _GroupStandardItem(QStandardItem):

    def __init__(self, group: GroupInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group = group

    def data(self, role: Qt.ItemDataRole) -> QVariant:
        if role == Qt.DisplayRole:
            return self._group.name()
        
        if role == Qt.DecorationRole:
            t = self._group.type()
            if t == Type.PASSWORD:
                return QIcon(":/icons/key")
            elif t == Type.CARD:
                return QIcon(":/icons/card")
            elif t == Type.IDENTITY:
                return QIcon(":/icons/id-card")

        if role == Qt.EditRole:
            return self._group.name()

        return QVariant()

    def setData(self, value: QVariant, role: Qt.ItemDataRole) -> None:
        if role != Qt.EditRole:
            return

        self._group.name(value)

    def flags(self) -> Qt.ItemFlags:
        return super().flags() | Qt.ItemIsEditable


class _DatabasesTreeModel(QStandardItemModel):

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return self.itemFromIndex(index).flags()


class DatabasesTree(QTreeView):

    databaseOpening = pyqtSignal(object)
    databaseSelected = pyqtSignal(object)
    groupSelected = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHeaderHidden(True)
        self.expandsOnDoubleClick()
        self.header().setStretchLastSection(True)
        self.setModel(_DatabasesTreeModel())
        self._databases = {}

    @pyqtSlot(DatabaseInterface)
    def addDatabase(self, database: DatabaseInterface) -> None:
        if database in self._databases:
            return

        item = _DatabaseStandardItem(database)
        self.model().appendRow(item)
        self._databases[database] = item

    @pyqtSlot(DatabaseInterface)
    def removeDatabase(self, database: DatabaseInterface) -> None:
        item = self._databases[database]
        self.model().removeRow(item.row())
        del self._databases[database]
        self.__emitSignals(None if not self._databases else self.model().item(0))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        if not index.isValid():
            event.ignore()
            return

        self.__emitSignals(self.model().itemFromIndex(index))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        if not index.isValid():
            event.ignore()
            return

        item = self.model().itemFromIndex(index)
        if type(item) is not _DatabaseStandardItem or item._database.status() != Status.CLOSED:
            return super().mouseDoubleClickEvent(event)

        self.databaseOpening.emit(item._database)
        event.accept()

    def __emitSignals(self, item: DatabaseInterface | GroupInterface) -> None:
        if type(item) is _DatabaseStandardItem and item._database.status() != Status.CLOSED:
            self.databaseSelected.emit(item._database)
            self.groupSelected.emit(None)
        elif type(item) is _GroupStandardItem:
            self.databaseSelected.emit(item._group.database())
            self.groupSelected.emit(item._group)
        else:
            self.databaseSelected.emit(None)
            self.groupSelected.emit(None)
