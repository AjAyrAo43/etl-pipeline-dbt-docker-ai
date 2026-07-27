import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from etl_pipeline import validate_dataframe

def test_validate_dataframe_valid():
    sample_data = pd.DataFrame({
        "year": [2023, 2022],
        "value": ["100", "200"],
        "units": ["Dollars", "Dollars"],
        "variable_code": ["H01", "H02"]
    })
    assert validate_dataframe(sample_data) is True

def test_validate_dataframe_missing_column():
    sample_data = pd.DataFrame({
        "year": [2023],
        "value": ["100"],
        "units": ["Dollars"]
        # Missing variable_code
    })
    assert validate_dataframe(sample_data) is False

def test_validate_dataframe_empty():
    sample_data = pd.DataFrame()
    assert validate_dataframe(sample_data) is False
