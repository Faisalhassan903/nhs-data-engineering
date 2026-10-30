import re
from html.parser import HTMLParser
from urllib.parse import urljoin



from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utlis.logger import get_logger
from config.settings import RAW_DATA_DIR

logger = get_logger(__name__)

NHS_PUBLICATION_URL = (
    "https://www.england.nhs.uk/statistics/"
    "statistical-work-areas/ae-waiting-times-and-activity/"
    "ae-attendances-and-emergency-admissions-2026-27/"
)


def create_session() -> requests.Session:
    """Create an HTTP session with retries for temporary failures."""

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


class LinkParser(HTMLParser):
    """Extract links and their visible text from an HTML page."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data):
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_href:
            text = " ".join(self.current_text).strip()
            self.links.append((text, self.current_href))

            self.current_href = None
            self.current_text = []


def discover_nhs_csvs(page_url: str) -> dict[str, str]:
    """Find monthly NHS A&E CSV links on a publication page."""

    logger.info("Checking NHS publication page: %s", page_url)

    with create_session() as session:
        response = session.get(page_url, timeout=(10, 60))
        response.raise_for_status()

    parser = LinkParser()
    parser.feed(response.text)

    datasets = {}

    pattern = re.compile(
        r"Monthly A&E\s+"
        r"(January|February|March|April|May|June|"
        r"July|August|September|October|November|December)"
        r"\s+(\d{4})",
        re.IGNORECASE,
    )

    for text, href in parser.links:
        match = pattern.search(text)

        if not match:
            continue

        if not re.search(r"\bCSV\b", text, re.IGNORECASE):
            continue

        month = match.group(1).lower()
        year = match.group(2)

        filename = f"ae_{month}_{year}.csv"
        download_url = urljoin(page_url, href)

        datasets[filename] = download_url

    logger.info("Discovered %s NHS CSV datasets", len(datasets))

    return datasets


def download_csv(
    url: str,
    destination: Path,
    overwrite: bool = False,
) -> Path:
    """Download a CSV safely without overwriting existing files."""

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not overwrite:
        logger.info("File already exists: %s", destination)
        return destination

    temp_path = destination.with_name(destination.name + ".part")

    logger.info("Starting download: %s", url)

    try:
        with create_session() as session:
            with session.get(
                url,
                timeout=(10, 60),
                stream=True,
            ) as response:
                response.raise_for_status()

                with temp_path.open("wb") as file:
                    for chunk in response.iter_content(
                        chunk_size=1024 * 1024
                    ):
                        if chunk:
                            file.write(chunk)

        if temp_path.stat().st_size == 0:
            raise ValueError("Downloaded file is empty")

        with temp_path.open("rb") as file:
            header = file.read(4096).lstrip().lower()

        if header.startswith((b"<html", b"<!doctype html", b"<?xml")):
            raise ValueError("Downloaded content is not a CSV file")

        temp_path.replace(destination)

        logger.info("Download successful: %s", destination)
        return destination

    except (requests.RequestException, OSError, ValueError):
        logger.exception("CSV download failed")
        raise

    finally:
        if temp_path.exists():
            temp_path.unlink()
if __name__ == "__main__":
    try:
        logger.info("NHS automated ingestion started")

        datasets = discover_nhs_csvs(NHS_PUBLICATION_URL)

        if not datasets:
            raise RuntimeError("No NHS datasets discovered")

        for filename, url in sorted(datasets.items()):
            destination = RAW_DATA_DIR / filename

            download_csv(
                url=url,
                destination=destination,
                overwrite=False,
            )

        logger.info("NHS dataset downloads completed")

    except Exception:
        logger.exception("NHS automated ingestion failed")
        raise