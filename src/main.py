#!/usr/bin/env python3
import os
import shutil

import sqlite3


LEGAL_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "tiff", "gif", "webp"]
DB_NAME = "paperless.db"


def _is_legal_extensions(file_path: str) -> bool:
    for ext in LEGAL_EXTENSIONS:
        if file_path.lower().endswith("." + ext):
            return True
    return False


def _file_exists_in_paperless(file_path: str, cursor) -> bool:
    res = cursor.execute(f"SELECT filename FROM inserted WHERE filename=?", (file_path,))
    return res.fetchone() != None


def _create_db():
    db =  sqlite3.connect(DB_NAME)
    cur = db.cursor()
    cur.execute("CREATE TABLE inserted(filename TEXT)")
    db.commit()
    db.close()


def _add_file(file_name: str, file_path: str, destination_folder: str, cursor):
    dst = os.path.join(destination_folder, file_name)
    shutil.copy(file_path, dst)
    cursor.execute("INSERT INTO inserted VALUES (?)", (file_path,))


def _copy_files(source_folder: str, destination_folder: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if not _is_legal_extensions(file_path):
                continue
            if _file_exists_in_paperless(file_path, cursor):
                continue
            print("Found supported file: ", file_path)
            _add_file(file_name, file_path, destination_folder, cursor)
            conn.commit()

    conn.close()


if __name__ == "__main__":
    src = os.getenv("PAPERLESS_SOURCE_FOLDER", "/home/OneDrive/Private")
    dst = os.getenv("PAPERLESS_CONSUME_FOLDER", "/docker/paperlessngx/consume")

    if not os.path.isfile(DB_NAME):
        print(f"DB {DB_NAME} does not exist, creating")
        _create_db()

    _copy_files(src, dst)
