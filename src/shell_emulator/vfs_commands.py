"""Служебные команды для работы с VFS: vfs-info и vfs-tree."""

from shell_emulator.results import GENERAL_ERROR_STATUS, USAGE_STATUS, Result
from shell_emulator.vfs import PATH_SEPARATOR, VfsError

TREE_MAX_ARGS = 1


def not_connected(name):
    """Результат-ошибка для случая, когда VFS не подключена."""
    return Result(
        error=f"{name}: VFS не подключена (запустите с --vfs)",
        status=GENERAL_ERROR_STATUS,
    )


def too_many_arguments(name):
    """Результат-ошибка для лишних аргументов команды."""
    return Result(error=f"{name}: too many arguments", status=USAGE_STATUS)


def handle_vfs_info(args, context):
    """vfs-info: показывает источник и сводку по загруженной VFS."""
    if args:
        return too_many_arguments("vfs-info")
    if context.vfs is None:
        return not_connected("vfs-info")
    stats = context.vfs.stats()
    lines = [
        f"source: {context.vfs.source_path}",
        f"directories: {stats.directories}",
        f"files: {stats.files}",
        f"total size: {stats.total_bytes} B",
        f"max depth: {stats.depth}",
    ]
    return Result(output="\n".join(lines))


def handle_vfs_tree(args, context):
    """vfs-tree [путь]: печатает дерево VFS от указанного пути."""
    if len(args) > TREE_MAX_ARGS:
        return too_many_arguments("vfs-tree")
    if context.vfs is None:
        return not_connected("vfs-tree")
    path = args[0] if args else PATH_SEPARATOR
    try:
        lines = context.vfs.tree_lines(path)
    except VfsError as error:
        return Result(
            error=f"vfs-tree: {error}", status=GENERAL_ERROR_STATUS
        )
    return Result(output="\n".join(lines))
