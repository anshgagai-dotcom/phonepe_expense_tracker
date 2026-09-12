"""
Load and manage application settings and environment variables safely.
"""
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger("PhonePeTracker")

def get_bundle_dir() -> Path:
    """Return bundle root directory (supports both standard Python and PyInstaller _MEIPASS)"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent

def get_runtime_dir() -> Path:
    """Directory for writable output and user config"""
    if hasattr(sys, "_MEIPASS"):
        return Path.cwd()
    return Path(__file__).resolve().parent.parent.parent

BASE_DIR = get_bundle_dir()
RUNTIME_DIR = get_runtime_dir()
ENV_FILE_PATH = RUNTIME_DIR / ".env"

def load_env_file(env_path: Path = ENV_FILE_PATH) -> None:
    """Read .env file variables into os.environ"""
    try:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"Error loading environment variables from {env_path}: {e}")

# Load environment on module import
load_env_file()

def get_budget_limit() -> float:
    """Return current budget limit from environment or default"""
    try:
        return float(os.getenv("BUDGET_LIMIT", "10000.0"))
    except ValueError:
        return 10000.0

def set_budget_limit(new_limit: float) -> bool:
    """Update budget limit in memory and persist to .env file"""
    try:
        os.environ["BUDGET_LIMIT"] = str(new_limit)
        lines = []
        key_found = False

        if ENV_FILE_PATH.exists():
            with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("BUDGET_LIMIT="):
                        lines.append(f"BUDGET_LIMIT={new_limit}\n")
                        key_found = True
                    else:
                        lines.append(line)
        if not key_found:
            lines.append(f"BUDGET_LIMIT={new_limit}\n")

        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        logger.error(f"Failed to persist budget limit: {e}")
        return False

BUDGET_LIMIT: float = get_budget_limit()

def resolve_data_file_path() -> Path:
    env_path = os.getenv("DATA_FILE_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    # Check current working directory
    cwd_path = Path.cwd() / "data" / "transactions.txt"
    if cwd_path.exists():
        return cwd_path
    # Check bundled path
    bundled_path = BASE_DIR / "data" / "transactions.txt"
    if bundled_path.exists():
        return bundled_path
    return cwd_path

DATA_FILE_PATH: Path = resolve_data_file_path()
OUTPUT_JSON_PATH: Path = RUNTIME_DIR / Path(os.getenv("OUTPUT_JSON_PATH", "data/summary.json"))
LOG_FILE_PATH: Path = RUNTIME_DIR / Path(os.getenv("LOG_FILE_PATH", "logs/tracker.log"))
