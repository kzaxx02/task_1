"""Виртуальная файловая система (VFS), целиком хранящаяся в памяти.

Источник VFS - каталог на диске. Он только читается: содержимое
загружается в память один раз, дальше диск не используется.
"""

import os
from dataclasses import dataclass, field

PATH_SEPARATOR = "/"
EMPTY_PART = ""
CURRENT_PART = "."
PARENT_PART = ".."
SKIPPED_PARTS = (EMPTY_PART, CURRENT_PART)
FIRST_LEVEL = 1
LEVEL_STEP = 1
FIRST_POSITION = 1
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE_INDENT = "│   "
BLANK_INDENT = "    "


class VfsError(Exception):
    """Ошибка загрузки VFS или обращения к её путям."""


@dataclass
class VfsFile:
    """Файл VFS: имя и содержимое, целиком загруженное в память."""

    name: str
    content: bytes = b""

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.content)


@dataclass
class VfsDirectory:
    """Каталог VFS: имя и дочерние узлы, индексированные по имени."""

    name: str
    children: dict = field(default_factory=dict)

    def add(self, node):
        """Добавляет дочерний узел."""
        self.children[node.name] = node

    def sorted_children(self):
        """Возвращает дочерние узлы, упорядоченные по имени."""
        return [self.children[name] for name in sorted(self.children)]


@dataclass(frozen=True)
class VfsStats:
    """Сводка по VFS (корневой каталог в счёт не входит)."""

    directories: int
    files: int
    total_bytes: int
    depth: int


def read_file(path, name):
    """Читает файл с диска целиком в память."""
    try:
        with open(path, "rb") as handle:
            content = handle.read()
    except OSError as error:
        reason = error.strerror or str(error)
        raise VfsError(f"не удалось прочитать {path}: {reason}") from error
    return VfsFile(name, content)


def load_entry(path, name):
    """Загружает файл или каталог.

    Символические ссылки и специальные файлы пропускаются (возвращается
    None): так нельзя выйти за пределы источника и зациклиться.
    """
    if os.path.islink(path):
        return None
    if os.path.isdir(path):
        return load_directory(path, name)
    if os.path.isfile(path):
        return read_file(path, name)
    return None


def load_directory(path, name):
    """Рекурсивно загружает каталог с диска в память."""
    try:
        entry_names = sorted(os.listdir(path))
    except OSError as error:
        reason = error.strerror or str(error)
        raise VfsError(f"не удалось прочитать {path}: {reason}") from error
    directory = VfsDirectory(name)
    for entry_name in entry_names:
        node = load_entry(os.path.join(path, entry_name), entry_name)
        if node is not None:
            directory.add(node)
    return directory


def walk_nodes(directory, level=FIRST_LEVEL):
    """Обходит всех потомков каталога, выдавая пары (уровень, узел)."""
    for node in directory.sorted_children():
        yield level, node
        if isinstance(node, VfsDirectory):
            yield from walk_nodes(node, level + LEVEL_STEP)


def normalize_parts(path):
    """Превращает путь в список имён с учётом "." и "..".

    Выше корня подняться нельзя: ".." в корне остаётся корнем.
    """
    parts = []
    for part in path.split(PATH_SEPARATOR):
        if part in SKIPPED_PARTS:
            continue
        if part == PARENT_PART:
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return parts


def describe_node(node):
    """Возвращает подпись узла: каталог со слешем или файл с размером."""
    if isinstance(node, VfsDirectory):
        return node.name + PATH_SEPARATOR
    return f"{node.name} ({node.size} B)"


def render_children(directory, prefix):
    """Строит строки дерева для потомков каталога."""
    lines = []
    children = directory.sorted_children()
    total = len(children)
    for position, child in enumerate(children, FIRST_POSITION):
        is_last = position == total
        branch = LAST_BRANCH if is_last else BRANCH
        lines.append(prefix + branch + describe_node(child))
        if isinstance(child, VfsDirectory):
            indent = BLANK_INDENT if is_last else PIPE_INDENT
            lines.extend(render_children(child, prefix + indent))
    return lines


class VirtualFileSystem:
    """VFS в памяти: корневой каталог и путь источника на диске."""

    def __init__(self, source_path, root):
        """Запоминает источник и загруженное дерево."""
        self.source_path = source_path
        self.root = root

    def resolve(self, path):
        """Находит узел по пути (от корня VFS); иначе VfsError."""
        if path == EMPTY_PART:
            raise VfsError("empty path: No such file or directory")
        node = self.root
        for part in normalize_parts(path):
            if not isinstance(node, VfsDirectory):
                raise VfsError(f"{path}: Not a directory")
            node = node.children.get(part)
            if node is None:
                raise VfsError(f"{path}: No such file or directory")
        return node

    def stats(self):
        """Считает каталоги, файлы, общий размер и глубину дерева."""
        directories = files = total_bytes = depth = 0
        for level, node in walk_nodes(self.root):
            depth = max(depth, level)
            if isinstance(node, VfsDirectory):
                directories += 1
            else:
                files += 1
                total_bytes += node.size
        return VfsStats(directories, files, total_bytes, depth)

    def tree_lines(self, path=PATH_SEPARATOR):
        """Возвращает строки дерева, начиная с узла по указанному пути."""
        node = self.resolve(path)
        header = PATH_SEPARATOR + PATH_SEPARATOR.join(normalize_parts(path))
        if isinstance(node, VfsFile):
            return [f"{header} ({node.size} B)"]
        return [header] + render_children(node, EMPTY_PART)


def load_vfs(source_path):
    """Загружает каталог на диске в память и возвращает VFS."""
    root = load_directory(source_path, EMPTY_PART)
    return VirtualFileSystem(source_path, root)
