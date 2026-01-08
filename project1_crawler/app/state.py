import json
from pathlib import Path
from typing import Any, Dict

def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(path: Path, data: Dict[str, Any]) -> None:
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    tmp.replace(path)
