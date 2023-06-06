
import os
import sqlite3
import typing
import json


import lib.core.data.item as libitem
import lib.core.data.factory as factory
from .database import DatabaseInterface, ClosedError, Status, SALT_LENGTH
from .data.group import GroupInterface

from lib.crypto import generate
from lib.crypto import cipher as libcipher
from lib.crypto import hasher as libhasher
from lib.crypto import encoder as libencoder


class _BaseState:

    def __init__(self, database: "SQLiteDatabase"):
        self._database = database


class _ClosedState(_BaseState):

    def __init__(self, database: "SQLiteDatabase"):
        super().__init__(database)
        self._loaded_previosly = False 

    def name(self, new_name: str = None) -> str | None:
        if new_name is None:
            return self._database._meta["name"]
        
        raise ClosedError("database closed")

    def status(self) -> Status:
        return Status.CLOSED

    def master_key(self, new_master_key: str = None) -> str | None:
        raise ClosedError("database closed")

    def hasher(self, new_hasher: libhasher.HashInterface = None) -> libhasher.HashInterface | None:
        raise ClosedError("database closed")

    def cipher(self, new_cipher: libcipher.CipherInterface = None) -> libcipher.CipherInterface | None:
        raise ClosedError("database closed")

    def encoder(self, new_encoder: libencoder.EncoderInterface = None) -> libencoder.EncoderInterface | None:
        raise ClosedError("database closed")

    def open(self, master_key: str) -> None:
        if not self._valid_master_key(master_key):
            raise ValueError("incorrect master key")

        if self._loaded_previosly:
            self._database._set_state(self._database._opened_state)
            return

        con = sqlite3.connect(self._database.location())
        cur = con.cursor()
        dec = self._decrypt_func(master_key)
        for group in self._load_groups(cur):
            self._load_items(cur, dec, group)
            self._database._groups[group.name()] = group

        self._loaded_previosly = True
        self._database._master_key = master_key
        self._database._set_state(self._database._opened_state)
        con.close()

    def close(self) -> None:
        ...

    def save(self) -> None:
        raise ClosedError("database closed")

    def group(self, name: str) -> "GroupInterface":
        raise ClosedError("database closed")

    def groups(self) -> typing.List["GroupInterface"]:
        raise ClosedError("database closed")

    def add_group(self, group: "GroupInterface") -> None:
        raise ClosedError("database closed")

    def remove(self) -> None:
        raise ClosedError("database closed")

    def remove_group(self, group: "GroupInterface") -> None:
        raise ClosedError("database closed")

    def _valid_master_key(self, master_key: str) -> bool:
        if self._database._master_key is not None:
            return self._database._master_key == master_key

        mkh = self._database._meta["master_key_hash"]
        h = self._database._meta["hasher"]
        e = self._database._meta["encoder"]
        hs = self._database._meta["hash_salt"]
        return mkh == e.encode(h.hash(master_key.encode(), hs))

    def _decrypt_func(self, master_key: str) -> typing.Callable[[bytes], str]:
        def decrypt(data: bytes):
            decoded = self._database._meta["encoder"].decode(data)
            decrypted = self._database._meta["cipher"].decrypt(
                decoded,
                master_key.encode(),
                self._database._meta["cipher_salt"]
            )
            return decrypted.decode('utf-8')

        return decrypt

    def _load_groups(self, cur) -> GroupInterface:
        res = cur.execute("SELECT name, type FROM `group`").fetchall()
        for r in res: 
            yield factory.group_from_type(r[1])(name=r[0], items=[])

    def _load_items(self, cur, dec: typing.Callable[[bytes], str], group: GroupInterface) -> None:
        res = cur.execute("SELECT id, data FROM item WHERE group_name = ?", [group.name()]).fetchall()
        for i in res:
            item = factory.item_from_type(group.type())(json.loads(dec(i[1])))
            item._set_id(res[0])
            group.add_item(item)


class _OpenedState(_BaseState):

    def name(self, new_name: str = None) -> str | None:
        if new_name is None:
            return self._database._meta["name"]
        elif new_name == self._database._meta["name"]:
            return

        self._database._meta["name"] = new_name
        self._database._set_state(self._database._modified_state)

    def status(self) -> Status:
        return Status.OPENED

    def master_key(self, new_master_key: str = None) -> str | None:
        if new_master_key is None:
            return self._database._master_key
        elif new_master_key == self._database._master_key:
            return

        self._database._master_key = new_master_key
        self._database._set_state(self._database._modified_state)


    def hasher(self, new_hasher: libhasher.HashInterface = None) -> libhasher.HashInterface | None:
        if new_hasher is None:
            return self._database._meta["hasher"]
        elif new_hasher == self._database._meta["hasher"]:
            return

        self._database._meta["hasher"] = new_hasher
        self._database._set_state(self._database._modified_state)

    def cipher(self, new_cipher: libcipher.CipherInterface = None) -> libcipher.CipherInterface | None:
        if new_cipher is None:
            return self._database._meta["cipher"]
        elif new_cipher == self._database._meta["cipher"]:
            return

        self._database._meta["cipher"] = new_cipher
        self._database._set_state(self._database._modified_state)

    def encoder(self, new_encoder: libencoder.EncoderInterface = None) -> libencoder.EncoderInterface | None:
        if new_encoder is None:
            return self._database._meta["encoder"]
        elif new_encoder == self._database._meta["encoder"]:
            return

        self._database._meta["encoder"] = new_encoder
        self._database._set_state(self._database._modified_state)

    def open(self, master_key: str) -> None:
        ...

    def close(self) -> None:
        self._database._set_state(self._database._closed_state)

    def save(self) -> None:
        ...

    def group(self, name: str) -> "GroupInterface":
        return self._database._groups[name]

    def groups(self) -> typing.List["GroupInterface"]:
        return list(self._database._groups.values())

    def add_group(self, group: "GroupInterface") -> None:
        if group.name() in self._database.groups():
            raise ValueError(f"Group with name {group.name()} already exist")

        self._database._groups[group.name()] = group
        self._database._set_state(self._database._modified_state)

    def remove(self) -> None:
        os.remove(self._database.location())

    def remove_group(self, group: "GroupInterface") -> None:
        if group.name() not in self._database._groups:
            raise ValueError(f"Group with name {group.name()} is not exist")

        del self._database._groups[group.name()]
        self._database._set_state(self._database._modified_state)


class _ModifiedState(_OpenedState):

    def status(self) -> Status:
        return Status.MODIFIED

    def save(self) -> None:
        con = sqlite3.connect(self._database.location())
        cur = con.cursor()
        self._save_meta(cur)
        encrypt = self._encrypt_func(cur)
        for group in self._database.groups():
            self._save_group(cur, group)
            for item in group.items():
                self._save_item(cur, encrypt, item)

        con.commit()
        self._database._set_state(self._database._opened_state)
        con.close()

    def _save_meta(self, cur) -> None:
        cur.execute("DELETE FROM meta") # clear previos meta data
        cur.execute("""
            INSERT INTO meta(name, master_key_hash, hash_salt, cipher_salt, hasher_id, cipher_id, encoder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            self._database._meta["name"],
            self._hash_master_key(),
            self._database._meta["hash_salt"],
            self._database._meta["cipher_salt"],
            self._database._meta["hasher"].id().value,
            self._database._meta["cipher"].id().value,
            self._database._meta["encoder"].id().value,
        ])

    def _hash_master_key(self) -> bytes:
        h = self._database._meta["hasher"]
        e = self._database._meta["encoder"]
        hs = self._database._meta["hash_salt"]
        return e.encode(h.hash(self._database._master_key.encode(), hs))

    def _encrypt_func(self, cur) -> typing.Callable[[str], bytes]:
        c = self._database._meta["cipher"]
        e = self._database._meta["encoder"]
        cs = self._database._meta["cipher_salt"]
        def encrypt(data: str) -> str:
            encrypted = c.encrypt(data.encode(), self._database._master_key.encode(), cs)
            encoded = e.encode(encrypted)
            return encoded

        return encrypt

    def _save_group(self, cur, group: GroupInterface) -> None:
        cur.execute("""
            INSERT OR IGNORE INTO `group`
            VALUES (?, ?)
        """, [group.name(), group.type().value])

    def _save_item(self, cur, encrypt_func: typing.Callable[[str], bytes], item: "ItemInterface") -> None:
        data = encrypt_func(json.dumps(item.data()))
        if item._id == libitem.NO_ID:
            res = cur.execute("""
                INSERT INTO item(group_name, data)
                VALUES (?, ?)
            """, [item.group().name(), data])
            item._set_id(res.lastrowid)
        else:
            cur.execute("""
                UPDATE item
                SET data = ?
                WHERE id = ?
            """, data, item._id)


class SQLiteDatabase(DatabaseInterface):

    @staticmethod
    def create(location: str, name: str, master_key: str, hasher: libhasher.HashInterface,
            cipher: libcipher.CipherInterface, encoder: libencoder.EncoderInterface) -> "SQLiteDatabase":
        hash_salt = generate.random_bytes(SALT_LENGTH)
        cipher_salt = generate.random_bytes(SALT_LENGTH)
        master_key_hash = encoder.encode(hasher.hash(master_key.encode(), hash_salt))
        con = sqlite3.connect(location)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                name TEXT NOT NULL,
                master_key_hash BLOB NOT NULL,
                hash_salt BLOB NOT NULL,
                cipher_salt BLOB,
                cipher_id TEXT NOT NULL,
                hasher_id TEXT NOT NULL,
                encoder_id TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS `group` (
                name TEXT PRIMARY KEY,
                type TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                data BLOB NOT NULL,

                FOREIGN KEY(group_name) REFERENCES `group`(name) ON DELETE CASCADE
            );
        """)
        cur.execute("""
            INSERT INTO meta(name, master_key_hash, hash_salt, cipher_salt, cipher_id, hasher_id, encoder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, [name, master_key_hash, hash_salt, cipher_salt, libcipher.ID(cipher.id()).value, libhasher.ID(hasher.id()).value, libencoder.ID(encoder.id()).value])
        con.commit()
        con.close()
        db = SQLiteDatabase(location)
        db._master_key = master_key
        db._set_state(db._opened_state)
        return db

    def __init__(self, location: str):
        super().__init__()
        self._location = location
        self._master_key = None
        self._groups = {}
        
        self._closed_state = _ClosedState(self)
        self._opened_state = _OpenedState(self)
        self._modified_state = _ModifiedState(self)
        self._current_state = self._closed_state
        
        self._load_meta()

    def location(self) -> str:
        return self._location

    def name(self, new_name: str = None) -> str | None:
        return self._current_state.name(new_name)

    def master_key(self, new_master_key: str = None) -> str | None:
        return self._current_state.master_key(new_master_key)

    def status(self) -> Status:
        return self._current_state.status()

    def hasher(self, new_hasher: libhasher.HashInterface = None) -> libhasher.HashInterface | None:
        return self._current_state.hasher(new_hasher)

    def cipher(self, new_cipher: libcipher.CipherInterface = None) -> libcipher.CipherInterface | None:
        return self._current_state.cipher(new_cipher)

    def encoder(self, new_encoder: libencoder.EncoderInterface = None) -> libencoder.EncoderInterface | None:
        return self._current_state.encoder(new_encoder)

    def open(self, master_key: str) -> None:
        self._current_state.open(master_key)

    def close(self) -> None:
        self._current_state.close()

    def save(self) -> None:
        self._current_state.save()

    def group(self, name: str) -> "GroupInterface":
        return self._current_state.group(name)

    def groups(self) -> typing.List["GroupInterface"]:
        return self._current_state.groups()

    def add_group(self, group: "GroupInterface") -> None:
        self._current_state.add_group(group)

    def remove(self) -> None:
        self._current_state.remove()

    def remove_group(self, group: "GroupInterface") -> None:
        self._current_state.remove_group(group)

    def _set_state(self, state: DatabaseInterface) -> None:
        if self._current_state == self._closed_state and state == self._modified_state:
            raise ValueError("Unsupported storage transtion from closed to modified state")

        self._current_state = state

    def _load_meta(self) -> None:
        con = sqlite3.connect(self.location())
        cur = con.cursor()
        res = cur.execute("""
            SELECT name, master_key_hash, hash_salt, cipher_salt, hasher_id, cipher_id, encoder_id
            FROM meta
        """).fetchone()
        self._meta = {
            "name": res[0],
            "master_key_hash": res[1],
            "hash_salt": res[2],
            "cipher_salt": res[3],
            "hasher": libhasher.from_id(res[4]),
            "cipher": libcipher.from_id(res[5]),
            "encoder": libencoder.from_id(res[6])
        }
        con.close()

    def __hash__(self) -> hash:
        return hash(self.location())