
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from lib.core.data.group import Type, GroupInterface, PasswordsGroup, CardsGroup, IdentitiesGroup
from lib.core.data.item import ItemInterface


class _PasswordsGroupModel(QAbstractTableModel):

    def __init__(self, group: PasswordsGroup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.headers = ["Title", "URL", "Login", "Email" , "Password", "Notes"]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> QVariant:
        if orientation == Qt.Vertical:
            return QVariant()
        
        if role == Qt.DisplayRole:
            return self.headers[section]
        elif role == Qt.DecorationRole:
            if section == 1:
                return QIcon(":/icons/url")
            elif section == 2:
                return QIcon(":/icons/user")
            elif section == 3:
                return QIcon(":/icons/email")
            elif section == 4:
                return QIcon(":/icons/key-solid")

        return QVariant()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if not index.isValid():
            return QVariant()

        item = self.group.items()[index.row()]
        if role == Qt.DisplayRole:
            if index.column() == 4:
                return "*" * len(item.entry("password"))

            return item.entry(self.headers[index.column()].lower())

        if role == Qt.TextAlignmentRole and index.column() == 4:
            return Qt.AlignCenter

        return QVariant()

    def rowCount(self, index: QModelIndex) -> int:
        return len(self.group.items())

    def columnCount(self, index: QModelIndex) -> int:
        return len(self.headers)


class _CardsGroupModel(QAbstractTableModel):

    def __init__(self, group: CardsGroup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.headers = ["Title", "Holder", "Number", "CVV", "Expiration", "Notes"]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> QVariant:
        if orientation == Qt.Vertical or role != Qt.DisplayRole:
            return QVariant()

        return self.headers[section]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            data = self.group.items()[index.row()].entry(self.headers[index.column()].lower())
            if index.column() == 3:
                return "*" * len(data)
            
            return data

        if role == Qt.TextAlignmentRole and index.column() == 3:
            return Qt.AlignCenter

    def rowCount(self, index: QModelIndex) -> int:
        return len(self.group)

    def columnCount(self, index: QModelIndex) -> int:
        return len(self.headers)


class _IdenitiesGroupModel(QAbstractTableModel):

    def __init__(self, group: IdentitiesGroup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.headers = ["Title", "Full Name", "Phone", "Email", "Notes"]

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> Qt.ItemDataRole:
        if orientation == Qt.Vertical or role != Qt.DisplayRole:
            return QVariant()

        return self.headers[section]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QVariant:
        if not index.isValid() or role != Qt.DisplayRole:
            return QVariant()

        item = self.group.items()[index.row()]
        key = "full_name" if index.column() == 1 else self.headers[index.column()].lower()
        return item.entry(key)

    def rowCount(self, index: QModelIndex) -> int:
        return len(self.group.items())

    def columnCount(self, index: QModelIndex) -> int:
        return len(self.headers)


class GroupTable(QTableView):

    createItem = pyqtSignal()
    itemSelected = pyqtSignal(ItemInterface)
    itemDoubleClicked = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(24)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        if not index.isValid():
            event.ignore()
            return

        item = self.model().group.items()[index.row()]
        self.itemSelected.emit(item)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.createItem.emit()
            return

        item = self.model().group.items()[index.row()]
        self.itemDoubleClicked.emit(item)
        event.accept()

    @pyqtSlot(GroupInterface)
    def load(self, group: GroupInterface) -> None:
        self.reset()
        if group.type() == Type.PASSWORD:
            self.setModel(_PasswordsGroupModel(group))
        elif group.type() == Type.CARD:
            self.setModel(_CardsGroupModel(group))
        elif group.type() == Type.IDENTITY:
            self.setModel(_IdenitiesGroupModel(group))
        else:
            raise Exception(f"Unsupported group type: {group.type().value}")

    @pyqtSlot(ItemInterface)
    def addItem(self, item: ItemInterface) -> None:
        m = self.model()
        m.beginInsertRows(QModelIndex(), len(m.group), len(m.group))
        m.group.add_item(item)
        m.endInsertRows()

    @pyqtSlot(ItemInterface)
    def removeItem(self, item: ItemInterface) -> None:
        m = self.model()
        pos = m.group.items().index(item)
        m.beginRemoveRows(QModelIndex(), pos, pos)
        m.group.remove_item(item)
        m.endRemoveRows()

    @pyqtSlot()
    def clear(self) -> None:
        m = self.model()
        m.beginRemoveRows(QModelIndex(), 0, len(m.group)-1)
        m.endRemoveRows()
        for item in m.group.items():
            m.group.remove_item(item)
