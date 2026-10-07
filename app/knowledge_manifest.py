import json
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = BASE_DIR / "knowledge" / "manifest.json"


@lru_cache(maxsize=1)
def source_metadata() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {item["filename"]: item for item in data.get("files", [])}
