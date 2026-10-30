import pandas as pd
import pytest

from src.utlis.exceptions import DataValidationError


def test_valid_schema(profile, sample_df):
    profile.validate_schema(sample_df)


@pytest.mark.parametrize("column", ["Period", "Org Code", "Org name", "A&E attendances Type 1"])
def test_missing_required_column(profile, sample_df, column):
    with pytest.raises(DataValidationError, match="Missing required columns"):
        profile.validate_schema(sample_df.drop(columns=column))


def test_profile_counts(profile, sample_df):
    assert profile.profile_data(sample_df) == {
        "total_rows": 3, "total_columns": 4, "duplicate_rows": 0,
        "missing_values": 0, "summary_rows": 1,
    }


def test_profile_missing_and_duplicates(profile, sample_df):
    sample_df.loc[0, "Org name"] = None
    frame = pd.concat([sample_df, sample_df.iloc[[1]]], ignore_index=True)
    report = profile.profile_data(frame)
    assert report["duplicate_rows"] == 1
    assert report["missing_values"] == 1


def test_clean_removes_summary_without_mutating_input(profile, sample_df):
    original = sample_df.copy(deep=True)
    result = profile.clean_data(sample_df)
    pd.testing.assert_frame_equal(result, original.iloc[:2])
    pd.testing.assert_frame_equal(sample_df, original)


@pytest.mark.parametrize("kind", ["empty", "summary_only", "missing_code", "duplicate_code"])
def test_clean_rejects_invalid_data(profile, sample_df, kind):
    if kind == "empty":
        sample_df = sample_df.iloc[:0]
    elif kind == "summary_only":
        sample_df = sample_df.iloc[2:]
    elif kind == "missing_code":
        sample_df.loc[0, "Org Code"] = None
    else:
        sample_df.loc[1, "Org Code"] = "AAA"
    with pytest.raises(DataValidationError):
        profile.clean_data(sample_df)


def test_load_missing_file(profile, tmp_path):
    with pytest.raises(FileNotFoundError):
        profile.load_data(tmp_path / "missing.csv")


def test_process_file(profile, sample_df, tmp_path, monkeypatch):
    source = tmp_path / "ae_april_2026.csv"
    sample_df.to_csv(source, index=False)
    before = source.read_bytes()
    output_dir = tmp_path / "processed"
    monkeypatch.setattr(profile, "PROCESSED_DATA_DIR", output_dir)
    output = profile.process_file(source)
    assert output == output_dir / "ae_april_2026_clean.csv"
    pd.testing.assert_frame_equal(pd.read_csv(output), sample_df.iloc[:2])
    assert source.read_bytes() == before


def test_batch_selects_only_monthly_files(profile, sample_df, tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    for name in ["ae_april_2026.csv", "ae_may_2026.csv", "download_test.csv"]:
        sample_df.to_csv(raw / name, index=False)
    monkeypatch.setattr(profile, "RAW_DATA_DIR", raw)
    monkeypatch.setattr(profile, "PROCESSED_DATA_DIR", tmp_path / "processed")
    outputs = profile.process_all_files()
    assert [p.name for p in outputs] == ["ae_april_2026_clean.csv", "ae_may_2026_clean.csv"]
    assert all(len(pd.read_csv(p)) == 2 for p in outputs)


def test_batch_empty_directory(profile, tmp_path, monkeypatch):
    monkeypatch.setattr(profile, "RAW_DATA_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="No NHS CSV files"):
        profile.process_all_files()
