"""Состояние сеанса оболочки, доступное всем командам."""

from dataclasses import dataclass
from typing import Optional

from shell_emulator.vfs import VirtualFileSystem


@dataclass
class ShellContext:
    """Изменяемое состояние сеанса: подключённая VFS (или None)."""

    vfs: Optional[VirtualFileSystem] = None
