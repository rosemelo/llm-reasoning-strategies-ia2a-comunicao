# utils/memory.py
import json
import os
from datetime import datetime

MEMORY_PATH = "memory.json"

def init_memory(path=MEMORY_PATH):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"qa": []}, f, ensure_ascii=False, indent=2)

def add_memory(question, answer, path=MEMORY_PATH):
    init_memory(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["qa"].append({
        "question": question,
        "answer": answer if isinstance(answer, str) else str(answer),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_memory(path=MEMORY_PATH, limit=50):
    init_memory(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["qa"][-limit:]
