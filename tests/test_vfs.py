"""Тесты виртуальной файловой системы."""

import contextlib
import os
import shutil
import tempfile
import unittest

from shell_emulator.vfs import VfsDirectory, VfsError, VfsFile, load_vfs

SAMPLE_FILES = {
    "a.txt": b"abc",
    "docs/guide.txt": b"hello",
    "docs/deep/x.txt": b"12",
}


def build_tree(folder, files):
    """Создаёт на диске файлы из словаря {относительный путь: байты}."""
    for relative, content in files.items():
        path = os.path.join(folder, *relative.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(content)


def snapshot(folder):
    """Снимок каталога: список путей и содержимое файлов."""
    result = {}
    for base, dirs, files in os.walk(folder):
        for name in dirs:
            result[os.path.join(base, name)] = None
        for name in files:
            path = os.path.join(base, name)
            with open(path, "rb") as handle:
                result[path] = handle.read()
    return result


class LoadTest(unittest.TestCase):
    """Загрузка каталога с диска в память."""

    def test_empty_directory(self):
        """Пустой каталог - пустая VFS."""
        with tempfile.TemporaryDirectory() as folder:
            vfs = load_vfs(folder)
        stats = vfs.stats()
        self.assertEqual(
            (stats.directories, stats.files, stats.total_bytes, stats.depth),
            (0, 0, 0, 0),
        )
        self.assertEqual(vfs.tree_lines(), ["/"])

    def test_nested_tree_stats(self):
        """Считаются каталоги, файлы, размер и глубина."""
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, SAMPLE_FILES)
            stats = load_vfs(folder).stats()
        self.assertEqual(stats.directories, 2)
        self.assertEqual(stats.files, 3)
        self.assertEqual(stats.total_bytes, 10)
        self.assertEqual(stats.depth, 3)

    def test_tree_lines(self):
        """Дерево печатается отсортированным, с размерами."""
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, SAMPLE_FILES)
            lines = load_vfs(folder).tree_lines()
        self.assertEqual(
            lines,
            [
                "/",
                "├── a.txt (3 B)",
                "└── docs/",
                "    ├── deep/",
                "    │   └── x.txt (2 B)",
                "    └── guide.txt (5 B)",
            ],
        )

    def test_binary_content_kept(self):
        """Содержимое хранится как байты без искажений."""
        data = bytes(range(256))
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, {"bin.dat": data})
            vfs = load_vfs(folder)
        node = vfs.resolve("/bin.dat")
        self.assertIsInstance(node, VfsFile)
        self.assertEqual(node.content, data)

    def test_source_is_not_a_directory(self):
        """Файл вместо каталога - VfsError."""
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, {"one.txt": b"x"})
            with self.assertRaises(VfsError):
                load_vfs(os.path.join(folder, "one.txt"))

    def test_source_missing(self):
        """Несуществующий источник - VfsError."""
        with self.assertRaises(VfsError):
            load_vfs("/no/such/source/dir")

    @unittest.skipUnless(hasattr(os, "symlink"), "нет символических ссылок")
    def test_symlinks_skipped(self):
        """Символические ссылки не попадают в VFS."""
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, {"real.txt": b"x"})
            os.symlink(
                os.path.join(folder, "real.txt"),
                os.path.join(folder, "link.txt"),
            )
            lines = load_vfs(folder).tree_lines()
        self.assertEqual(lines, ["/", "└── real.txt (1 B)"])


class InMemoryTest(unittest.TestCase):
    """VFS живёт в памяти и не меняет диск."""

    def test_works_after_source_removed(self):
        """После удаления каталога VFS остаётся полной."""
        folder = tempfile.mkdtemp()
        build_tree(folder, SAMPLE_FILES)
        vfs = load_vfs(folder)
        shutil.rmtree(folder)
        self.assertEqual(vfs.stats().files, 3)
        self.assertEqual(vfs.resolve("/docs/guide.txt").content, b"hello")

    def test_disk_not_modified(self):
        """Загрузка и просмотр не меняют файлы на диске."""
        with tempfile.TemporaryDirectory() as folder:
            build_tree(folder, SAMPLE_FILES)
            before = snapshot(folder)
            vfs = load_vfs(folder)
            vfs.stats()
            vfs.tree_lines("/docs")
            after = snapshot(folder)
        self.assertEqual(before, after)


@contextlib.contextmanager
def sample_vfs():
    """Создаёт тестовое дерево на диске и отдаёт (каталог, VFS)."""
    with tempfile.TemporaryDirectory() as folder:
        build_tree(folder, SAMPLE_FILES)
        yield folder, load_vfs(folder)


class ResolveTest(unittest.TestCase):
    """Поиск узлов по путям."""

    def test_root_variants(self):
        """Корень задаётся по-разному."""
        with sample_vfs() as (folder, vfs):
            for path in ("/", "//", "/.", "/docs/..", "/.."):
                self.assertIs(vfs.resolve(path), vfs.root, path)

    def test_relative_to_root(self):
        """Путь без ведущего слеша считается от корня."""
        with sample_vfs() as (folder, vfs):
            node = vfs.resolve("docs/deep")
        self.assertIsInstance(node, VfsDirectory)
        self.assertEqual(node.name, "deep")

    def test_dots(self):
        """Точки и двойные точки учитываются."""
        with sample_vfs() as (folder, vfs):
            node = vfs.resolve("/docs/./deep/../guide.txt")
        self.assertEqual(node.name, "guide.txt")

    def test_missing(self):
        """Несуществующий путь - ошибка."""
        with sample_vfs() as (folder, vfs):
            with self.assertRaises(VfsError) as caught:
                vfs.resolve("/docs/nope")
        self.assertIn("No such file or directory", str(caught.exception))

    def test_through_file(self):
        """Проход через файл - ошибка Not a directory."""
        with sample_vfs() as (folder, vfs):
            with self.assertRaises(VfsError) as caught:
                vfs.resolve("/a.txt/inside")
        self.assertIn("Not a directory", str(caught.exception))

    def test_empty_path(self):
        """Пустой путь - ошибка."""
        with sample_vfs() as (folder, vfs):
            with self.assertRaises(VfsError):
                vfs.resolve("")

    def test_tree_of_file_and_subdir(self):
        """Дерево строится от файла и от подкаталога."""
        with sample_vfs() as (folder, vfs):
            self.assertEqual(vfs.tree_lines("/a.txt"), ["/a.txt (3 B)"])
            self.assertEqual(
                vfs.tree_lines("/docs/deep"),
                ["/docs/deep", "└── x.txt (2 B)"],
            )


if __name__ == "__main__":
    unittest.main()
