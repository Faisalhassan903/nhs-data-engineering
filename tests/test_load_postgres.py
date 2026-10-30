from unittest.mock import MagicMock
import pandas as pd
import pytest
from src.ingestion import load_postgres as loader


def sample_frame():
    return pd.DataFrame([{key: ('April 2026' if i == 0 else 'AAA' if i < 4 else 10)
                          for i, key in enumerate(loader.COLUMN_MAPPING)}])


def test_prepare_rejects_duplicate_period_org(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, 'PROCESSED_DATA_DIR', tmp_path)
    pd.concat([sample_frame(), sample_frame()]).to_csv(tmp_path / 'ae_april_clean.csv', index=False)
    with pytest.raises(ValueError, match='Duplicate period'):
        loader.prepare_data()


def test_prepare_rejects_missing_columns(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, 'PROCESSED_DATA_DIR', tmp_path)
    sample_frame().drop(columns=['Period']).to_csv(tmp_path / 'ae_april_clean.csv', index=False)
    with pytest.raises(ValueError, match='missing columns'):
        loader.prepare_data()


def test_loader_uses_configured_database_and_parameter_values(monkeypatch):
    connect = MagicMock()
    cursor = connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1
    monkeypatch.setattr(loader.psycopg, 'connect', connect)
    monkeypatch.setenv('PGDATABASE', 'test_nhs')
    monkeypatch.setenv('PGHOST', 'test-host')
    frame = sample_frame().rename(columns=loader.COLUMN_MAPPING)
    assert loader.load_to_postgres(frame) == 1
    connect.assert_called_once_with(dbname='test_nhs', host='test-host')
    query, rows = cursor.executemany.call_args.args
    assert 'ON CONFLICT' in query.as_string()
    assert rows == [tuple(frame.iloc[0])]
