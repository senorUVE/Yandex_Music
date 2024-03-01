from contextlib import contextmanager
from typing import Iterator
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Engine
from getpass import getpass


class DatabaseConnector:
    def __init__(self,
                 db_host: str, db_port: int,
                 db_name: str, db_user: str,
                 db_password: str,
                 db_connect_timeout: float,
                ):
        self._db_host = db_host
        self._db_port = db_port
        self._db_name = db_name
        self._db_user = db_user
        self._db_password = db_password
        self._db_connect_timeout = db_connect_timeout

        self._create_sessionmakers()

    def _create_sessionmakers(self) -> Engine:
        db_url = f"postgresql://{self._db_user}:{self._db_password}@/{self._db_name}?host={self._db_host}:{self._db_port}"
        self._master_engine = create_engine(
            url=db_url,
            connect_args=dict(target_session_attrs="read-write"),
            # echo=True
        )
        self._master_sessionmaker = sessionmaker(
            bind=self._master_engine,
            expire_on_commit=False,
        )

    @contextmanager
    def get_master_session(self) -> Iterator[Session]:
        with self._master_sessionmaker.begin() as session:
            try:
                yield session
            except Exception as e:
                print(e)
                raise


def make_connector() -> DatabaseConnector:
    return DatabaseConnector(
        # писалось за ночь, забыл вынести хотя бы переменные окружения...
    )
