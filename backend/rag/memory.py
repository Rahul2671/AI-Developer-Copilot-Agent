import os
import json

MEMORY_DIR = "data/conversations"
MAX_TURNS = 10  # keep last 10 exchanges (20 messages) per project


def _memory_path(project_id):
    return f"{MEMORY_DIR}/{project_id}.json"


def get_history(project_id):
    path = _memory_path(project_id)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def append_turn(project_id, question, answer):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    history = get_history(project_id)
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    history = history[-(MAX_TURNS * 2):]

    with open(_memory_path(project_id), "w", encoding="utf-8") as f:
        json.dump(history, f)


def clear_history(project_id):
    path = _memory_path(project_id)
    if os.path.exists(path):
        os.remove(path)
