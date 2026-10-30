from src.ingestion.download_ae import (
    NHS_PUBLICATION_URL,
    discover_nhs_csvs,
    download_csv,
)
from src.ingestion.profile_ae import process_all_files
from src.utlis.logger import get_logger
from config.settings import RAW_DATA_DIR


logger = get_logger(__name__)


def run_pipeline() -> None:
    """Run the NHS A&E ingestion and cleaning pipeline."""

    logger.info("NHS end-to-end pipeline started")

    try:
        # Stage 1: Discover datasets
        datasets = discover_nhs_csvs(NHS_PUBLICATION_URL)

        if not datasets:
            raise RuntimeError("No NHS datasets discovered")

        logger.info("Discovered %s datasets", len(datasets))

        # Stage 2: Download missing datasets
        for filename, url in sorted(datasets.items()):
            destination = RAW_DATA_DIR / filename

            download_csv(
                url=url,
                destination=destination,
                overwrite=False,
            )

        # Stage 3: Validate, profile and clean
        processed_files = process_all_files()

        logger.info(
            "NHS pipeline completed successfully: %s processed files",
            len(processed_files),
        )

    except Exception:
        logger.exception("NHS pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()