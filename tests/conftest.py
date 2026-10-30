"""Synthetic test data and isolated ingestion modules."""
import importlib
import logging

import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Period": ["April 2026"] * 3,
        "Org Code": ["AAA", "BBB", "TOTAL"],
        "Org name": ["Example Trust A", "Example Trust B", "England"],
        "A&E attendances Type 1": [10, 20, 30],
    })


@pytest.fixture
def ingestion_modules(monkeypatch):
    # Avoid opening production log files when modules are first imported.
    from src.utlis import logger
    monkeypatch.setattr(logger, "get_logger", logging.getLogger)
    profile = importlib.import_module("src.ingestion.profile_ae")
    download = importlib.import_module("src.ingestion.download_ae")
    return profile, download


@pytest.fixture
def profile(ingestion_modules):
    return ingestion_modules[0]


@pytest.fixture
def download(ingestion_modules):
    return ingestion_modules[1]
