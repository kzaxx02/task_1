"""Формирование приглашения к вводу по данным реальной ОС."""

import getpass
import socket

DEFAULT_USER = "user"
DEFAULT_HOST = "localhost"
HOME_MARK = "~"


def get_username():
    """Возвращает имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return DEFAULT_USER


def get_hostname():
    """Возвращает короткое имя компьютера (до первой точки)."""
    full_name = socket.gethostname() or DEFAULT_HOST
    return full_name.split(".")[0]


def build_prompt():
    """Собирает приглашение вида username@hostname:~$ ."""
    user = get_username()
    host = get_hostname()
    return f"{user}@{host}:{HOME_MARK}$ "
