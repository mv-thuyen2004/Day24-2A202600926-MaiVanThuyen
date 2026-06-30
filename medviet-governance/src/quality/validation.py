# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    TODO: Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context()
    try:
        suite = context.suites.get("patient_data_suite")
    except Exception:
        suite = ExpectationSuite(name="patient_data_suite")
        suite = context.suites.add(suite)

    # Lấy validator
    df = pd.read_csv("data/raw/patients_raw.csv")
    batch = context.data_sources.pandas_default.read_dataframe(df)
    validator = context.get_validator(batch=batch, expectation_suite=suite)

    # --- TASK: Thêm các expectations ---

    # 1. patient_id không được null
    validator.expect_column_values_to_not_be_null("patient_id")

    # 2. TODO: cccd phải có đúng 12 ký tự
    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    # 3. TODO: ket_qua_xet_nghiem phải trong khoảng [0, 50]
    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    )

    # 4. TODO: benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    # 5. TODO: email phải match regex pattern
    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"    # TODO: email regex
    )

    # 6. TODO: Không được có duplicate patient_id
    validator.expect_column_values_to_be_unique(column="patient_id")

    context.suites.add_or_update(validator.expectation_suite)
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    TODO: Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath, dtype=str)
    df_raw = pd.read_csv("data/raw/patients_raw.csv", dtype=str)
    
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy
    # (sau anonymization, cccd phải là fake hoặc masked)
    original_cccds = set(df_raw["cccd"].astype(str))
    anon_cccds = set(df["cccd"].astype(str))
    overlap = original_cccds.intersection(anon_cccds)
    if len(overlap) > 0:
        results["success"] = False
        results["failed_checks"].append("Check 1 Failed: Original CCCD values found in anonymized output")

    # Check 2: Không có null values trong các cột quan trọng
    critical_cols = ["patient_id", "ho_ten", "cccd", "so_dien_thoai", "email"]
    for col in critical_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                results["success"] = False
                results["failed_checks"].append(f"Check 2 Failed: Column '{col}' contains {null_count} null values")

    # Check 3: Số rows phải bằng original
    if len(df) != len(df_raw):
        results["success"] = False
        results["failed_checks"].append("Check 3 Failed: Row count does not match raw data")

    return results
