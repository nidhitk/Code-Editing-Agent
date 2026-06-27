import os
import hashlib
import shutil


BACKUP_DIR = ".backup"


def _backup_paths(file_path):
    absolute_path = os.path.abspath(file_path)
    digest = hashlib.sha1(absolute_path.encode("utf-8")).hexdigest()
    filename = os.path.basename(file_path)

    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{digest}.bak")
    sentinel_path = os.path.join(BACKUP_DIR, f"{filename}.{digest}.new")

    return backup_path, sentinel_path


def create_backup(file_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)

    backup_path, sentinel_path = _backup_paths(file_path)

    if os.path.exists(backup_path) or os.path.exists(sentinel_path):
        return

    if os.path.exists(file_path):
        shutil.copy(file_path, backup_path)
        return

    with open(sentinel_path, "w", encoding="utf-8"):
        pass


def rollback_file(file_path):
    backup_path, sentinel_path = _backup_paths(file_path)

    if os.path.exists(backup_path):
        shutil.copy(backup_path, file_path)
        return

    if os.path.exists(sentinel_path) and os.path.exists(file_path):
        os.remove(file_path)
