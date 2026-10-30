import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"

DATASET_FILENAME = os.getenv(
    "NHS_DATASET_FILENAME",
    "ae_april_2026.csv"
)

RAW_FILE_PATH = RAW_DATA_DIR / DATASET_FILENAME

PROCESSED_FILE_PATH = (
    PROCESSED_DATA_DIR / f"{Path(DATASET_FILENAME).stem}_clean.csv"
)

for directory in (RAW_DATA_DIR, PROCESSED_DATA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)