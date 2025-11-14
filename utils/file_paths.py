from pathlib import Path

# Root directory of the project (where main_app.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def raw(filename: str) -> Path:
    """Return path to a raw Patseer CSV."""
    return RAW_DIR / filename


def processed(filename: str) -> Path:
    """Return path to a processed CSV (output of scripts)."""
    return PROCESSED_DIR / filename
