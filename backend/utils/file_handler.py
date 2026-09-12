"""
Safe file I/O operations for reading statements and writing summaries.
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("PhonePeTracker")

def read_text_file(file_path: Path | str) -> list[str]:
    """Read a text file and return a list of lines safely"""
    path = Path(file_path)
    if path.exists():
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    else:
        logger.error(f"File not found: {path}")
        return []

def write_json_file(data: dict[str, Any], output_path: Path | str) -> None:
    """Write dictionary data to a formatted JSON file safely"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Data successfully written to {path}")
