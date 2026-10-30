from pathlib import Path

import pandas as pd

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utlis.logger import get_logger
from src.utlis.exceptions import DataValidationError


# Required NHS A&E dataset columns
REQUIRED_COLUMNS = {
    "Period",
    "Org Code",
    "Org name",
    "A&E attendances Type 1",
}

logger = get_logger(__name__)


def load_data(file_path: Path) -> pd.DataFrame:
    """Load an NHS A&E CSV file."""

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    logger.info("Loaded %s: %s rows", file_path.name, len(df))

    return df


def validate_schema(df: pd.DataFrame) -> None:
    """Check that required NHS columns exist."""

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise DataValidationError(
            f"Missing required columns: {sorted(missing_columns)}"
        )


def profile_data(df: pd.DataFrame) -> dict:
    """Generate a basic data-quality report."""

    report = {
        "total_rows": df.shape[0],
        "total_columns": df.shape[1],
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_values": int(df.isna().sum().sum()),
        "summary_rows": int(
    df["Org Code"].astype("string").str.strip().str.upper().eq("TOTAL").sum()
),
    }

    return report

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove summary rows and validate organisation codes."""

    # Normalise temporarily for validation
    org_codes = df["Org Code"].astype(str).str.strip().str.upper()

    # Remove TOTAL rows, regardless of case
    cleaned_df = df.loc[org_codes != "TOTAL"].copy()

    if cleaned_df.empty:
        raise DataValidationError("Cleaned dataset is empty")

    # Check missing organisation codes
    if cleaned_df["Org Code"].isna().any():
        raise DataValidationError("Missing organisation codes found")

    # Check empty organisation codes
    if cleaned_df["Org Code"].astype(str).str.strip().eq("").any():
        raise DataValidationError("Empty organisation codes found")

    # Check duplicate organisation codes
    cleaned_codes = (
        cleaned_df["Org Code"].astype(str).str.strip().str.upper()
    )

    if cleaned_codes.duplicated().any():
        raise DataValidationError("Duplicate organisation codes found")

    logger.info("All data-quality checks passed")

    return cleaned_df


def process_file(file_path: Path) -> Path:
    """Validate, profile, clean and save one NHS dataset."""

    logger.info("Processing dataset: %s", file_path.name)

    # 1. Load
    df = load_data(file_path)

    # 2. Validate schema
    validate_schema(df)

    # 3. Profile original data
    report = profile_data(df)

    logger.info(
        "Data profile for %s: %s",
        file_path.name,
        report,
    )

    # 4. Clean and validate
    cleaned_df = clean_data(df)

    # 5. Create output path
    output_path = (
        PROCESSED_DATA_DIR
        / f"{file_path.stem}_clean.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 6. Save cleaned dataset
    cleaned_df.to_csv(
        output_path,
        index=False,
    )

    logger.info(
        "Saved cleaned dataset: %s (%s rows)",
        output_path.name,
        len(cleaned_df),
    )

    return output_path


def process_all_files() -> list[Path]:
    """Process every monthly NHS A&E CSV in the raw directory."""

    files = sorted(RAW_DATA_DIR.glob("ae_*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No NHS CSV files found in {RAW_DATA_DIR}"
        )

    logger.info("Found %s NHS datasets", len(files))

    processed_files = []

    for file_path in files:
        output_path = process_file(file_path)
        processed_files.append(output_path)

    return processed_files


if __name__ == "__main__":
    logger.info("NHS batch processing started")

    try:
        processed_files = process_all_files()

        logger.info(
            "NHS batch processing completed successfully: %s files",
            len(processed_files),
        )

    except Exception:
        logger.exception("NHS batch processing failed")
        raise