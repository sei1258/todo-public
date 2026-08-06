import json
import os
from pathlib import Path


# Fletからアプリ用データフォルダを取得する。
# 普通のpythonコマンドで起動した場合は、ユーザーフォルダを予備に使う。
DATA_DIR = Path(
    os.environ.get(
        "FLET_APP_STORAGE_DATA",
        Path.home() / ".forge_todo",
    )
)

# フォルダがなければ作る
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "forge_todo_data.json"


def load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)