
import os
import typing
import appdirs
import yaml

from .sqlite_database import SQLiteDatabase


CONFIG_FILE = "config.yaml"


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self._config_dir = appdirs.user_config_dir("Kee", "")
        self._config_path = os.path.join(self._config_dir, CONFIG_FILE)
        self._databases = []
        self._read()

    def databases(self) -> typing.List[SQLiteDatabase]:
        return self._databases

    def add_database(self, database: SQLiteDatabase) -> None:
        self._databases.append(database)
        self._save()

    def remove_database(self, database: SQLiteDatabase) -> None:
        self._databases.remove(database)
        self._save()

    def _read(self) -> None:
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir)

        if not os.path.exists(self._config_path):
            open(self._config_path, "x").close()

        with open(self._config_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            if config is None:
                return

            if "databases" in config:
                self._databases = [SQLiteDatabase(loc) for loc in config["databases"]]

    def _save(self) -> None:
        print(self._databases)
        with open(self._config_path, "w") as yaml_file:
            data = {
                "databases": [db.location() for db in self._databases]
            }
            yaml.safe_dump(data, yaml_file)
