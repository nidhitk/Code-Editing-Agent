import os
import shutil


BACKUP_DIR = ".backup"


def create_backup(file_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)

    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)

    shutil.copy(file_path, backup_path)


def rollback_file(file_path):
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)

    if os.path.exists(backup_path):
        shutil.copy(backup_path, file_path)