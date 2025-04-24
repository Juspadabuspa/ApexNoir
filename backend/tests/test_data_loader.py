# backend/tests/test_data_loader.py

import pytest
from backend.src.utils.data_loader import get_df, _load_all_csvs

def test_load_all_csvs_contains_known_keys(tmp_path, monkeypatch):
    # Create a fake CSV file in a temp data dir
    fake_csv = tmp_path / "data" / "foo.csv"
    fake_csv.parent.mkdir()
    fake_csv.write_text("a,b\n1,2\n3,4\n")

    # Monkey-patch DATA_DIR to point at tmp_path/data
    from backend.src.utils import data_loader
    monkeypatch.setattr(data_loader, "DATA_DIR", fake_csv.parent)

    dfs = _load_all_csvs()
    assert "foo" in dfs
    df = dfs["foo"]
    assert list(df.columns) == ["a", "b"]
    assert df.shape == (2, 2)

def test_get_df_invalid_name_raises():
    with pytest.raises(KeyError):
        get_df("does_not_exist")
