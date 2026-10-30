from unittest.mock import MagicMock

import pytest
import requests


def mock_http(monkeypatch, download, *, text="", chunks=()):
    response = MagicMock()
    response.text = text
    response.iter_content.return_value = iter(chunks)
    response.__enter__.return_value = response
    session = MagicMock()
    session.__enter__.return_value = session
    session.get.return_value = response
    monkeypatch.setattr(download, "create_session", lambda: session)
    return session, response


def test_discovery_filters_links_and_resolves_relative_urls(download, monkeypatch):
    html = """
    <a href="/files/april.csv">Monthly A&amp;E <b>April 2026</b> CSV</a>
    <a href="https://example.test/may.csv">Monthly A&amp;E May 2026 CSV</a>
    <a href="/april.xlsx">Monthly A&amp;E April 2026 XLSX</a>
    <a href="/other.csv">Unrelated CSV</a>
    """
    mock_http(monkeypatch, download, text=html)
    assert download.discover_nhs_csvs("https://example.test/publication/") == {
        "ae_april_2026.csv": "https://example.test/files/april.csv",
        "ae_may_2026.csv": "https://example.test/may.csv",
    }


def test_discovery_no_matches(download, monkeypatch):
    mock_http(monkeypatch, download, text="<p>No datasets</p>")
    assert download.discover_nhs_csvs("https://example.test/") == {}


def test_discovery_http_failure(download, monkeypatch):
    _, response = mock_http(monkeypatch, download)
    response.raise_for_status.side_effect = requests.HTTPError("503")
    with pytest.raises(requests.HTTPError):
        download.discover_nhs_csvs("https://example.test/")


def test_download_writes_chunks(download, monkeypatch, tmp_path):
    mock_http(monkeypatch, download, chunks=[b"a,b\n", b"", b"1,2\n"])
    destination = tmp_path / "raw" / "data.csv"
    assert download.download_csv("https://example.test/data.csv", destination) == destination
    assert destination.read_bytes() == b"a,b\n1,2\n"
    assert not destination.with_suffix(".csv.part").exists()


def test_existing_file_skips_network(download, monkeypatch, tmp_path):
    session, _ = mock_http(monkeypatch, download)
    destination = tmp_path / "data.csv"
    destination.write_bytes(b"original")
    assert download.download_csv("https://example.test/data.csv", destination) == destination
    session.get.assert_not_called()
    assert destination.read_bytes() == b"original"


@pytest.mark.parametrize("payload", [b"", b"<html>Error</html>", b"<!DOCTYPE html>", b"<?xml version='1.0'?>"])
def test_invalid_download_preserves_existing_file(download, monkeypatch, tmp_path, payload):
    mock_http(monkeypatch, download, chunks=[payload])
    destination = tmp_path / "data.csv"
    destination.write_bytes(b"original")
    with pytest.raises(ValueError):
        download.download_csv("https://example.test/data.csv", destination, overwrite=True)
    assert destination.read_bytes() == b"original"
    assert not destination.with_suffix(".csv.part").exists()


def test_interrupted_download_cleans_partial_file(download, monkeypatch, tmp_path):
    def broken_stream():
        yield b"a,b\n"
        raise requests.ConnectionError("connection interrupted")
    mock_http(monkeypatch, download, chunks=broken_stream())
    destination = tmp_path / "data.csv"
    with pytest.raises(requests.ConnectionError):
        download.download_csv("https://example.test/data.csv", destination)
    assert not destination.exists()
    assert not destination.with_suffix(".csv.part").exists()


def test_overwrite_success(download, monkeypatch, tmp_path):
    mock_http(monkeypatch, download, chunks=[b"a,b\n1,2\n"])
    destination = tmp_path / "data.csv"
    destination.write_bytes(b"original")
    download.download_csv("https://example.test/data.csv", destination, overwrite=True)
    assert destination.read_bytes() == b"a,b\n1,2\n"
