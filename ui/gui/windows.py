
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import lib.crypto.encoder as encoder
import lib.crypto.hasher as hasher
import lib.crypto.cipher as cipher
import lib.crypto.generate as generate
import lib.core.data.factory as factory
from lib.core.config import Config
from lib.core.database import Status, DatabaseInterface
from lib.core.sqlite_database import SQLiteDatabase
from lib.core.data.group import Type, GroupInterface
from lib.core.data.item import ItemInterface, PasswordItem, CardItem, IdentityItem
from . import line_edits, dialogs, trees, tables, widgets


DEFAULT_CIPHER = cipher.AES_CBC
DEFAULT_HASHER = hasher.SHA256
DEFAULT_ENCODER = encoder.Base64


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Config()
        self.__clipboard = QApplication.clipboard()
        self.setWindowTitle("Kee")
        self.resize(750, 500)
        self.__initActions()
        self.__initUI()
        self.__initMenu()
        self.__initConnections()
        self.__setCurrentDatabase(None)
        self.__setCurrentGroup(None)
        self.__setCurrentItem(None)
    
    def __initActions(self) -> None:
        self.__actions = {
            "exit": QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"), triggered=QApplication.exit),

            # database actions
            "new-database": QAction("New", self, shortcut=QKeySequence("Ctrl+N")),
            "open-database": QAction("Open", self, shortcut=QKeySequence("Ctrl+O")),
            "close-database": QAction("Close", self, shortcut=QKeySequence("Ctrl+D")),
            "remove-database": QAction("Remove", self, shortcut=QKeySequence("Ctrl+R")),
            "save-database": QAction("Save", self, shortcut=QKeySequence("Ctrl+S")),
            "save-database-as": QAction("Save As...", self, shortcut=QKeySequence("Ctrl+Shift+S")),
            "database-settings": QAction("Database Settings...", self),
            "change-master-key": QAction("Change Master Key...", self),
            
            # group actions
            "add-group-passwords": QAction("Passwords", self),
            "add-group-cards": QAction("Cards", self),
            "add-group-identities": QAction("Identities", self),
            "rename-group": QAction("Rename...", self),
            "remove-group": QAction("Remove", self),
            "clear-group": QAction("Clear", self),

            # item actions
            "add-item": QAction("Add", self, shortcut=QKeySequence("Ctrl+Shift+N")),
            "remove-item": QAction("Remove", self, shortcut=QKeySequence("Delete")),
            "edit-item": QAction("Edit", self, shortcut=QKeySequence("Ctrl+E")),

            # item type specific
            "password-copy-login": QAction("Copy Login", self),
            "password-copy-password": QAction("Copy Password", self),
            "password-open-url": QAction("Open URL..."),

            "card-copy-number": QAction("Copy Number", self),
            "card-copy-cvv": QAction("Copy CVV", self),
            "card-copy-holder": QAction("Copy Holder", self),
        }

    def __initMenu(self) -> None:
        database_menu = self.menuBar().addMenu("Database")
        database_menu.addAction(self.__actions["new-database"])
        database_menu.addAction(self.__actions["open-database"])
        database_menu.addAction(self.__actions["close-database"])
        database_menu.addAction(self.__actions["remove-database"])
        database_menu.addSeparator()
        database_menu.addAction(self.__actions["save-database"])
        database_menu.addAction(self.__actions["save-database-as"])
        database_menu.addSeparator()
        database_menu.addAction(self.__actions["database-settings"])
        database_menu.addAction(self.__actions["change-master-key"])
        database_menu.addSeparator()
        database_menu.addAction(self.__actions["exit"])

        group_menu = self.menuBar().addMenu("Group")
        group_add = group_menu.addMenu("Add")
        group_menu.addSeparator()
        group_add.addAction(self.__actions["add-group-passwords"])
        group_add.addAction(self.__actions["add-group-cards"])
        group_add.addAction(self.__actions["add-group-identities"])
        group_menu.addAction(self.__actions["remove-group"])
        group_menu.addAction(self.__actions["clear-group"])
        group_menu.addAction(self.__actions["rename-group"])

        menu_item = self.menuBar().addMenu("Item")
        menu_item.addAction(self.__actions["add-item"])
        menu_item.addAction(self.__actions["remove-item"])
        menu_item.addAction(self.__actions["edit-item"])
        self.__menu_password = menu_item.addMenu("Password")
        self.__menu_password.addAction(self.__actions["password-copy-login"])
        self.__menu_password.addAction(self.__actions["password-copy-password"])
        self.__menu_password.addAction(self.__actions["password-open-url"])
        self.__menu_card = menu_item.addMenu("Card")
        self.__menu_card.addAction(self.__actions["card-copy-number"])
        self.__menu_card.addAction(self.__actions["card-copy-cvv"])
        self.__menu_card.addAction(self.__actions["card-copy-holder"])

    def __initUI(self) -> None:
        self.__tbl_group = tables.GroupTable()
        self.__tree_databases = trees.DatabasesTree()
        for db in Config().databases():
            self.__tree_databases.addDatabase(db)

        wgt_main = QSplitter()
        wgt_main.addWidget(self.__tree_databases)
        wgt_main.addWidget(self.__tbl_group)
        wgt_main.setSizes([200, 550])
        self.setCentralWidget(wgt_main)

    def __initConnections(self) -> None:
        self.__actions["exit"].triggered.connect(QApplication.exit)
        self.__actions["new-database"].triggered.connect(self.__newDatabase)
        self.__actions["open-database"].triggered.connect(self.__openDatabase)
        self.__actions["close-database"].triggered.connect(self.__closeDatabase)
        self.__actions["remove-database"].triggered.connect(self.__removeDatabase)
        self.__actions["remove-database"].triggered.connect(self.__tree_databases.viewport().update)
        self.__actions["save-database"].triggered.connect(lambda: self.__database.save())
        self.__actions["save-database"].triggered.connect(self.__tree_databases.viewport().update)
        self.__actions["database-settings"].triggered.connect(lambda: DatabaseSettingsWindow(self.__database).exec_())
        self.__actions["change-master-key"].triggered.connect(self.__changeMasterKey)
        self.__actions["add-group-passwords"].triggered.connect(lambda: self.__addGroup(Type.PASSWORD))
        self.__actions["add-group-cards"].triggered.connect(lambda: self.__addGroup(Type.CARD))
        self.__actions["add-group-identities"].triggered.connect(lambda: self.__addGroup(Type.IDENTITY))
        self.__actions["rename-group"].triggered.connect(self.__renameGroup)
        self.__actions["remove-group"].triggered.connect(self.__removeGroup)
        self.__actions["clear-group"].triggered.connect(self.__clearGroup)
        self.__actions["add-item"].triggered.connect(lambda: self.__editItem(self.__item))
        self.__actions["remove-item"].triggered.connect(lambda: self.__removeItem(self.__item))
        self.__actions["edit-item"].triggered.connect(lambda: self.__editItem(self.__item))
        self.__actions["password-open-url"].triggered.connect(lambda: QDesktopServices.openUrl(QUrl(self.__item.entry("url"))))
        self.__actions["password-copy-login"].triggered.connect(lambda: self.__clipboard.setText(self.__item.entry("login")))
        self.__actions["password-copy-password"].triggered.connect(lambda: self.__clipboard.setText(self.__item.entry("password")))
        self.__actions["card-copy-holder"].triggered.connect(lambda: self.__clipboard.setText(self.__item.entry("holder")))
        self.__actions["card-copy-cvv"].triggered.connect(lambda: self.__clipboard.setText(self.__item.entry("cvv")))
        self.__actions["card-copy-number"].triggered.connect(lambda: self.__clipboard.setText(self.__item.entry("number")))

        self.__tree_databases.databaseOpening.connect(self.__unlockDatabase)
        self.__tree_databases.databaseSelected.connect(self.__setCurrentDatabase)
        self.__tree_databases.groupSelected.connect(self.__setCurrentGroup)

        self.__tbl_group.itemSelected.connect(self.__setCurrentItem)
        self.__tbl_group.itemDoubleClicked.connect(self.__editItem)

    @pyqtSlot()
    def __newDatabase(self) -> None:
        win = NewDatabaseWindow(self)
        win.databaseCreated.connect(Config().add_database)
        win.databaseCreated.connect(self.__tree_databases.addDatabase)
        win.exec_()

    @pyqtSlot()
    def __openDatabase(self) -> None:
        dlg = dialogs.OpenDatabaseDialog(self)
        if not dlg.exec_():
            return

        self.__tree_databases.addDatabase(SQLiteDatabase(dlg.location()))

    @pyqtSlot()
    def __removeDatabase(self) -> None:
        delete = QMessageBox.question(
            self,
            "Remove Database",
            f"Are you shure you want to remove database \"{self.__database.name()}\""
        )
        if delete == QMessageBox.No:
            return

        Config().remove_database(self.__database)
        self.__database.remove()
        self.__tree_databases.removeDatabase(self.__database)

    @pyqtSlot()
    def __closeDatabase(self) -> None:
        self.__database.close()
        self.__setCurrentDatabase(None)
        self.__tree_databases.viewport().update()

    @pyqtSlot()
    def __changeMasterKey(self) -> None:
        change = QMessageBox.question(self, "Change Master Key", "Are you shure you want change master key?")
        if change == QMessageBox.No:
            return

        master_key = QInputDialog.getText(self, "Change Master Key", "New master key: ", QLineEdit.Password)[0]
        if not master_key:
            QMessageBox.critical(self, "Change Master Key", "Empty master key is not allowed")
            return

        self.__database.master_key(master_key)

    @pyqtSlot()
    def __removeGroup(self) -> None:
        remove = QMessageBox.question(
            self,
            "Remove Group",
            f"Are you shure you want remove group \"{self.__group.name()}\""
        )
        if remove == QMessageBox.No:
            return

        self.__tree_databases.removeGroup(self.__group)

    @pyqtSlot()
    def __renameGroup(self) -> None:
        new_name = QInputDialog.getText(self, "Raname Group", "New group name: ", QLineEdit.Normal)[0]
        if not new_name:
            QMessageBox.critical(self, "Raname Group", "Empty group name is not allowd")
            return

        self.__group.name(new_name)

    @pyqtSlot()
    def __clearGroup(self) -> None:
        clear = QMessageBox.question(
            self,
            "Clear Group",
            f"Are you shure you want clear group \"{self.__group.name()}\""
        )
        if clear == QMessageBox.No:
            return

        self.__tbl_group.clear()
        self.__tree_databases.viewport().update()
        self.__setCurrentItem(None)

    @pyqtSlot(ItemInterface)
    def __editItem(self, item: ItemInterface) -> None:
        if self.__group.type() == Type.PASSWORD:
            win = EditPasswordWindow(self, item=item)
        elif self.__group.type() == Type.CARD:
            win = EditCardWindow(self, item=item)
        elif self.__group.type() == Type.IDENTITY:
            win = EditIdentityWindow(self, item=item)
        else:
            return

        if item is None:
            win.itemCreated.connect(self.__tbl_group.addItem)

        win.exec_()

    @pyqtSlot(ItemInterface)
    def __removeItem(self, item: ItemInterface) -> None:
        remove = QMessageBox.question(self, "Remove Item", "Are you shure you want remove item?")
        if remove == QMessageBox.No:
            return

        self.__tbl_group.removeItem(self.__item)
        self.__tree_databases.viewport().update()

    @pyqtSlot(DatabaseInterface)
    def __setCurrentDatabase(self, database: DatabaseInterface) -> None:
        self.__database = database
        actions = [
            "close-database",
            "remove-database",
            "save-database",
            "save-database-as",
            "database-settings",
            "change-master-key",
            "add-group-cards",
            "add-group-passwords",
            "add-group-identities",
        ]
        for action in actions:
            self.__actions[action].setEnabled(database is not None)
        self.__setCurrentItem(None)

    @pyqtSlot(GroupInterface)
    def __setCurrentGroup(self, group: GroupInterface) -> None:
        self.__group = group
        actions = [
            "clear-group",
            "remove-group",
            "rename-group",
            "add-item"
        ]
        for action in actions:
            self.__actions[action].setEnabled(group is not None)

        if group is not None:
            self.__tbl_group.load(group)

    @pyqtSlot(ItemInterface)
    def __setCurrentItem(self, item: ItemInterface) -> None:
        self.__item = item
        not_none = self.__item is not None
        self.__actions["remove-item"].setEnabled(not_none)
        self.__actions["edit-item"].setEnabled(not_none)
        self.__menu_password.setEnabled(not_none and item.group().type() is Type.PASSWORD)
        self.__menu_card.setEnabled(not_none and item.group().type() is Type.CARD)

    @pyqtSlot(DatabaseInterface)
    def __unlockDatabase(self, database: DatabaseInterface) -> None:
        master_key = QInputDialog.getText(self, "Database Opening...", "Master Key: ", QLineEdit.Password)[0]
        if not master_key:
            return

        try:
            database.open(master_key)
            self.__setCurrentDatabase(database)
        except ValueError:
            QMessageBox.critical(self, "Database Opening...", "Specified master key is incorrect")

    @pyqtSlot(Type)
    def __addGroup(self, group_type: Type) -> None:
        name = QInputDialog.getText(self, "New Group", "Enter group name: ", QLineEdit.Normal)[0]
        if not name:
            QMessageBox.critical(self, "New Group", "Empty group name is not allowed")
            return

        group = factory.group_from_type(group_type.value)
        if group is None:
            QMessageBox.critical(self, "New Group", "Internal error\nUnknown group type")
            return

        self.__database.add_group(group(name=name, items=[]))


class NewDatabaseWindow(QDialog):

    databaseCreated = pyqtSignal(DatabaseInterface)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = None
        self.__initUI()

    def __initUI(self) -> None:
        self.resize(300, 250)
        self.setWindowTitle("New Database")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__edt_location = line_edits.SelectFileLineEdit(dialog=dialogs.SaveDatabaseDialog(), readOnly=True)
        self.__edt_name = QLineEdit()
        self.__edt_master_key = line_edits.PasswordLineEdit()
        self.__edt_repeated_key = line_edits.PasswordLineEdit()
        self.__btn_generate_key = QPushButton(QIcon(":/icons/generate"), "", toolTip="Generate Master Key", clicked=self.__generateKey)
        self.__btn_create = QPushButton(QIcon(":/icons/create"), "", toolTip="Create", clicked=self.__createDatabase)
        self.__chk_additional = QCheckBox("Additional", stateChanged=lambda st: self.__lyt_additional.setVisible(st == Qt.Checked))
        self.__lyt_additional = QWidget(visible=False)
        self.__cbx_hash = QComboBox()
        self.__cbx_cipher = QComboBox()
        self.__cbx_encoder = QComboBox()

        self.__cbx_hash.addItems([i.value for i in hasher.ID])
        self.__cbx_cipher.addItems([i.value for i in cipher.ID])
        self.__cbx_encoder.addItems([i.value for i in encoder.ID])
        self.__cbx_hash.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.__cbx_cipher.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.__cbx_encoder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        lyt_data = QFormLayout()
        lyt_data.addRow(QLabel("Location"), self.__edt_location)
        lyt_data.addRow(QLabel("Name"), self.__edt_name)
        lyt_data.addRow(QLabel("Master Key"), self.__edt_master_key)
        lyt_data.addRow(QLabel("Repeat Key"), self.__edt_repeated_key)

        lyt_additional = QFormLayout()
        lyt_additional.setContentsMargins(0, 0, 0, 0)
        lyt_additional.addRow(QLabel("Hash"), self.__cbx_hash)
        lyt_additional.addRow(QLabel("Encryption"), self.__cbx_cipher)
        lyt_additional.addRow(QLabel("Encoding"), self.__cbx_encoder)
        self.__lyt_additional.setLayout(lyt_additional)

        lyt_contols = QHBoxLayout()
        lyt_contols.addWidget(self.__chk_additional)
        lyt_contols.addStretch()
        lyt_contols.addWidget(self.__btn_generate_key)
        lyt_contols.addWidget(self.__btn_create)

        lyt_main = QVBoxLayout()
        lyt_main.addLayout(lyt_data)
        lyt_main.addSpacing(8)
        lyt_main.addWidget(self.__lyt_additional)
        lyt_main.addLayout(lyt_contols)

        self.setLayout(lyt_main)

    @pyqtSlot()
    def __generateKey(self) -> None:
        key = generate.password(16)
        self.__edt_master_key.setText(key)
        self.__edt_repeated_key.setText(key)

    @pyqtSlot()
    def __createDatabase(self) -> None:
        msg = self.__errorMessage()
        if msg is not None:
            msg.exec_()
            return

        additional = self.__chk_additional.checkState() == Qt.Checked
        hasher_ = hasher.from_id(self.__cbx_hash.currentText())
        cipher_ = cipher.from_id(self.__cbx_cipher.currentText())
        encoder_ = encoder.from_id(self.__cbx_encoder.currentText())
        try:
            database = SQLiteDatabase.create(
                location=self.__edt_location.text(),
                name=self.__edt_name.text(),
                master_key=self.__edt_master_key.text(),
                hasher=hasher_ if additional else DEFAULT_HASHER,
                cipher=cipher_ if additional else DEFAULT_CIPHER,
                encoder=encoder_ if additional else DEFAULT_ENCODER
            )
        except Exception as e:
            msg = QMessageBox(
                self,
                windowTitle="Internal error", 
                icon=QMessageBox.Critical,
                text="Error occurs while database creating...",
                informativeText=str(e),
            )
            msg.exec_()
            return

        self.databaseCreated.emit(database)
        self.accept()

    def __errorMessage(self) -> QMessageBox | None:
        msg = QMessageBox(self, windowTitle="Error", icon=QMessageBox.Critical, text="Invalid Data", standardButtons=QMessageBox.Ok)
        if not self.__edt_location.text():
            msg.setInformativeText("Database location is not specified")
        elif not self.__edt_name.text():
            msg.setInformativeText("Database name cannot be empty")
        elif not self.__edt_master_key.text():
            msg.setInformativeText("Master key should be specified")
        elif self.__edt_master_key.text() != self.__edt_repeated_key.text():
            msg.setInformativeText("Master key and repeated key is not equal")

        return msg if msg.informativeText() else None


class DatabaseSettingsWindow(QDialog):

    databaseChanged = pyqtSignal(DatabaseInterface)

    def __init__(self, database: DatabaseInterface, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database = database
        self.__initUI()

    def __initUI(self) -> None:
        self.resize(300, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Database Settings")
        wgt_tab = QTabWidget()
        wgt_tab.addTab(self.__generalTab(), "General")
        wgt_tab.addTab(self.__secureTab(), "Secure")
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.rejected.connect(self.reject)
        btn_box.accepted.connect(self.__save)

        lyt_main = QVBoxLayout(spacing=7)
        lyt_main.addWidget(wgt_tab)
        lyt_main.addWidget(btn_box)
        self.setLayout(lyt_main)

    def __generalTab(self) -> QWidget:
        self.__edt_name = QLineEdit(self._database.name())
        self.__edt_location = QLineEdit(self._database.location(), readOnly=True)
        lyt = QFormLayout()
        lyt.addRow(QLabel("Database Name"), self.__edt_name)
        lyt.addRow(QLabel("Database Location"), self.__edt_location)
        lyt.addRow(QLabel("Groups Count"), QLabel(str(len(self._database.groups()))))
        wgt = QWidget()
        wgt.setLayout(lyt)
        return wgt

    def __secureTab(self) -> QWidget:
        self.__cbx_hasher = QComboBox()
        self.__cbx_cipher = QComboBox()
        self.__cbx_encoder = QComboBox()

        self.__cbx_hasher.addItems([i.value for i in hasher.ID])
        self.__cbx_cipher.addItems([i.value for i in cipher.ID])
        self.__cbx_encoder.addItems([i.value for i in encoder.ID])

        self.__cbx_hasher.setCurrentText(self._database.hasher().id().value)
        self.__cbx_cipher.setCurrentText(self._database.cipher().id().value)
        self.__cbx_encoder.setCurrentText(self._database.encoder().id().value)

        self.__cbx_hasher.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.__cbx_cipher.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.__cbx_encoder.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        lyt = QFormLayout()
        lyt.addRow(QLabel("Hash"), self.__cbx_hasher)
        lyt.addRow(QLabel("Encryption"), self.__cbx_cipher)
        lyt.addRow(QLabel("Encoding"), self.__cbx_encoder)
        wgt = QWidget()
        wgt.setLayout(lyt)
        return wgt

    def __errorMessage(self) -> QMessageBox:
        msg = QMessageBox(self, icon=QMessageBox.Critical, windowTitle="Database Settings.", text="Invalid data")
        if not self.__edt_name.text():
            msg.setInformativeText("Empty database name is not allowed")

        return msg if msg.informativeText() else None

    @pyqtSlot()
    def __save(self) -> None:
        msg = self.__errorMessage()
        if msg is not None:
            msg.exec_()
            return

        self._database.name(self.__edt_name.text())
        self._database.hasher(hasher.from_id(self.__cbx_hasher.currentText()))
        self._database.cipher(cipher.from_id(self.__cbx_cipher.currentText()))
        self._database.encoder(encoder.from_id(self.__cbx_encoder.currentText()))
        self.databaseChanged.emit(self._database)
        self.accept()


class EditPasswordWindow(QDialog):

    itemCreated = pyqtSignal(ItemInterface)

    def __init__(self, *args, item: ItemInterface = None, **kwargs): 
        super().__init__(*args, **kwargs)
        self.__item = item
        self.setWindowTitle(f"{'New' if item is None else 'Edit'} Password")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__item = item
        self.__edt_title = QLineEdit(item.entry("title") if item else "")
        self.__edt_url = QLineEdit(item.entry("url") if item else "https://")
        self.__edt_login = QLineEdit(item.entry("login") if item else "")
        self.__edt_email = QLineEdit(item.entry("email") if item else "")
        self.__edt_password = line_edits.PasswordLineEdit(item.entry("password") if item else "")
        self.__mem_notes = QTextEdit(item.entry("notes") if item else "")
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.__save)
        btn_box.rejected.connect(self.reject)

        lyt_edits = QFormLayout()
        lyt_edits.addRow(QLabel("Title"), self.__edt_title)
        lyt_edits.addRow(QLabel("URL"), self.__edt_url)
        lyt_edits.addRow(QLabel("Login"), self.__edt_login)
        lyt_edits.addRow(QLabel("Email"), self.__edt_email)
        lyt_edits.addRow(QLabel("Password"), self.__edt_password)

        lyt_memo = QVBoxLayout()
        lyt_memo.addWidget(QLabel("Notes"))
        lyt_memo.addWidget(self.__mem_notes)

        lyt_main = QVBoxLayout()
        lyt_main.addLayout(lyt_edits)
        lyt_main.addLayout(lyt_memo)
        lyt_main.addWidget(btn_box)

        self.setLayout(lyt_main)

    def __save(self) -> None:
        msg = self.__errorMessage()
        if msg is not None:
            msg.exec_()
            return

        data = {
            "title": self.__edt_title.text(),
            "url": self.__edt_url.text(),
            "login": self.__edt_login.text(),
            "email": self.__edt_email.text(),
            "password": self.__edt_password.text(),
            "notes": self.__mem_notes.toPlainText()
        }
        if not self.__item:
            self.__item = PasswordItem(data)
            self.itemCreated.emit(self.__item)
        else:
            for k, v in data.items():
                self.__item.entry(k, v)

        self.accept()

    def __errorMessage(self) -> QMessageBox:
        msg = QMessageBox(self, icon=QMessageBox.Critical, windowTitle=self.windowTitle(), text="Invalid data")
        if not PasswordItem.check_url(self.__edt_url.text()):
            msg.setInformativeText("URL format is not valid\nAcceptable format <protocol>/<hostname>\nExample: https://website.com")
        elif not PasswordItem.check_login(self.__edt_login.text()):
            msg.setInformativeText("Empty login is not allowed")
        elif not PasswordItem.check_password(self.__edt_password.text()):
            msg.setInformativeText("Empty password is not allowed")

        return None if not msg.informativeText() else msg


class EditCardWindow(QDialog):

    itemCreated = pyqtSignal(CardItem)

    def __init__(self, *args, item: CardItem = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"{'New' if item is None else 'Edit'} Card")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__item = item
        self.__edt_title = QLineEdit(item.entry("title") if item else "")
        self.__edt_number = QLineEdit(item.entry("number") if item else "", inputMask="0000 0000 0000 0000")
        self.__edt_cvv = QLineEdit(item.entry("cvv") if item else "", inputMask="0000")
        self.__wgt_expiration = widgets.ExpirationDateWidget(text=item.entry("expiration") if item else "")
        self.__edt_holder = QLineEdit(item.entry("holder") if item else "")
        self.__mem_notes = QTextEdit(item.entry("notes") if item else "")
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.__save)
        btn_box.rejected.connect(self.reject)

        lyt_edits = QFormLayout()
        lyt_edits.addRow(QLabel("Title"), self.__edt_title)
        lyt_edits.addRow(QLabel("Number"), self.__edt_number)
        lyt_edits.addRow(QLabel("CVV"), self.__edt_cvv)
        lyt_edits.addRow(QLabel("Expiration"), self.__wgt_expiration)
        lyt_edits.addRow(QLabel("Holder"), self.__edt_holder)

        lyt_notes = QVBoxLayout()
        lyt_notes.addWidget(QLabel("Notes"))
        lyt_notes.addWidget(self.__mem_notes)

        lyt_main = QVBoxLayout()
        lyt_main.addLayout(lyt_edits)
        lyt_main.addLayout(lyt_notes)
        lyt_main.addWidget(btn_box)
        self.setLayout(lyt_main)

    def __save(self) -> None:
        msg = self.__errorMessage()
        if msg is not None:
            msg.exec_()
            return

        data = {
            "title": self.__edt_title.text(),
            "number": self.__edt_number.text(),
            "cvv": self.__edt_cvv.text(),
            "expiration": self.__wgt_expiration.text(),
            "holder": self.__edt_holder.text(),
            "notes": self.__mem_notes.toPlainText()
        }
        if self.__item is None:
            self.__item = CardItem(data)
            self.itemCreated.emit(self.__item)
        else:
            for k, v in data.items():
                self.__item.entry(k, v)

        self.accept()

    def __errorMessage(self) -> QMessageBox:
        msg = QMessageBox(self, icon=QMessageBox.Critical, windowTitle=self.windowTitle(), text="Invalid data")
        if not CardItem.check_number(self.__edt_number.text()):
            msg.setInformativeText("Card number invalid format.\nExample: 1234 1234 1234 1234")
        elif not CardItem.check_cvv(self.__edt_cvv.text()):
            msg.setInformativeText("Card CVV number invalid format.\nExample 1234")

        return None if not msg.informativeText() else msg


class EditIdentityWindow(QDialog):

    itemCreated = pyqtSignal(IdentityItem)

    def __init__(self, *args, item: IdentityItem = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(f"{'New' if item is None else 'Edit'} Identity")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.__item = item
        self.__edt_title = QLineEdit(item.entry("title") if item else "")
        self.__edt_full_name = QLineEdit(item.entry("full_name") if item else "")
        self.__edt_phone = QLineEdit(item.entry("phone") if item else "", inputMask="+0 000 000-00-00")
        self.__edt_email = QLineEdit(item.entry("email") if item else "")
        self.__mem_notes = QTextEdit(item.entry("notes") if item else "")
        btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.__save)
        btn_box.rejected.connect(self.reject)

        lyt_edits = QFormLayout()
        lyt_edits.addRow(QLabel("Title"), self.__edt_title)
        lyt_edits.addRow(QLabel("Full name"), self.__edt_full_name)
        lyt_edits.addRow(QLabel("Phone"), self.__edt_phone)
        lyt_edits.addRow(QLabel("Email"), self.__edt_email)

        lyt_notes = QVBoxLayout()
        lyt_notes.addWidget(QLabel("Notes"))
        lyt_notes.addWidget(self.__mem_notes)

        lyt_main = QVBoxLayout()
        lyt_main.addLayout(lyt_edits)
        lyt_main.addLayout(lyt_notes)
        lyt_main.addWidget(btn_box)
        self.setLayout(lyt_main)

    def __save(self) -> None:
        msg = self.__errorMessage()
        if msg is not None:
            msg.exec_()
            return

        data = {
            "title": self.__edt_title.text(),
            "full_name": self.__edt_full_name.text(),
            "phone": self.__edt_phone.text(),
            "email": self.__edt_email.text(),
            "notes": self.__mem_notes.toPlainText()
        }
        if self.__item is None:
            self.__item = IdentityItem(data)
            self.itemCreated.emit(self.__item)
        else:
            for k, v in data.items():
                self.__item.entry(k, v)

        self.accept()

    def __errorMessage(self) -> QMessageBox:
        msg = QMessageBox(self, icon=QMessageBox.Critical, windowTitle=self.windowTitle(), text="Invalid data")
        if not IdentityItem.check_full_name(self.__edt_full_name.text()):
            msg.setInformativeText("Full name cannot be empty")

        return None if not msg.informativeText() else msg
