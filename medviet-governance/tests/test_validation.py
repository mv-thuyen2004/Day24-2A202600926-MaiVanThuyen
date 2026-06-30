# tests/test_validation.py
import pytest
from src.quality.validation import build_patient_expectation_suite, validate_anonymized_data

def test_validation_suite():
    suite = build_patient_expectation_suite()
    assert suite is not None
    assert suite.name == "patient_data_suite"

def test_validate_anonymized_data():
    res = validate_anonymized_data("data/processed/patients_anonymized.csv")
    assert res["success"] is True
    assert len(res["failed_checks"]) == 0
    assert res["stats"]["total_rows"] == 200
