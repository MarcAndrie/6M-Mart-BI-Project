
import pandas as pd
import numpy as np
import config

# ==========================================
# 1. LOAD DATASETS
# ==========================================

df_returns = pd.read_csv(
    config.RAW_DATA_DIR / "fact_returns.csv"
)

df_sales = pd.read_csv(
    config.RAW_DATA_DIR / "fact_sales.csv"
)

df_dates = pd.read_csv(
    config.RAW_DATA_DIR / "dim_date.csv"
)

df_branches = pd.read_csv(
    config.RAW_DATA_DIR / "dim_branches.csv"
)

df_products = pd.read_csv(
    config.RAW_DATA_DIR / "dim_products.csv"
)

df_dates["full_date"] = pd.to_datetime(
    df_dates["full_date"]
)

print("RETURNS DATA VALIDATION STARTED")
print("=" * 45)

# ==========================================
# 2. VALIDATION HELPER
# ==========================================

total_checks = 0
passed_checks = 0
failed_checks = 0


def check(condition, name, details=None):
    global total_checks, passed_checks, failed_checks

    total_checks += 1

    if condition:
        passed_checks += 1
        print(f"[PASS] {name}")
    else:
        failed_checks += 1
        print(f"[FAIL] {name}")

    if details is not None:
        print(f"       {details}")


# ==========================================
# 3. RECORD COUNT AND ID VALIDATION
# ==========================================

check(
    len(df_returns) > 0,
    "Returns dataset is not empty"
)

check(
    df_returns["return_id"].nunique() == len(df_returns),
    "Return ID uniqueness"
)

check(
    df_returns["return_id"].notna().all(),
    "Return ID completeness"
)

check(
    len(df_returns.columns) == 7,
    "Returns dataset has 7 columns"
)

# ==========================================
# 4. REQUIRED FIELD VALIDATION
# ==========================================

required_columns = [
    "return_id",
    "sales_line_id",
    "date_id",
    "branch_id",
    "product_id",
    "returned_quantity",
    "refund_amount"
]

missing_values = df_returns[required_columns].isna().sum().sum()

check(
    missing_values == 0,
    "Required fields have no missing values",
    f"Missing values found: {missing_values}"
)

# ==========================================
# 5. FOREIGN KEY VALIDATION
# ==========================================

check(
    df_returns["sales_line_id"].isin(
        df_sales["sales_line_id"]
    ).all(),
    "Original sales line foreign keys"
)

check(
    df_returns["date_id"].isin(
        df_dates["date_id"]
    ).all(),
    "Date foreign keys"
)

check(
    df_returns["branch_id"].isin(
        df_branches["branch_id"]
    ).all(),
    "Branch foreign keys"
)

check(
    df_returns["product_id"].isin(
        df_products["product_id"]
    ).all(),
    "Product foreign keys"
)

# ==========================================
# 6. RETURN EVENT VALIDATION
# ==========================================

check(
    df_returns["sales_line_id"].is_unique,
    "One return event per original sales line"
)

check(
    (
        df_returns["returned_quantity"] >= 1
    ).all(),
    "Returned quantities are at least 1"
)

check(
    (
        df_returns["returned_quantity"]
        == df_returns["returned_quantity"].astype(int)
    ).all(),
    "Returned quantities are whole numbers"
)

# ==========================================
# 7. MATCH RETURNS TO ORIGINAL SALES
# ==========================================

sales_reference = df_sales[
    [
        "sales_line_id",
        "branch_id",
        "product_id",
        "quantity",
        "gross_sales",
        "discount_amount",
        "date_id"
    ]
].copy()

matched_returns = df_returns.merge(
    sales_reference,
    on="sales_line_id",
    how="left",
    suffixes=("_return", "_sale"),
    indicator=True
)

# Check original sale references
check(
    (matched_returns["_merge"] == "both").all(),
    "Every return matches an original sale"
)

# Check branch consistency
check(
    (
        matched_returns["branch_id_return"]
        == matched_returns["branch_id_sale"]
    ).all(),
    "Return branch matches original sale"
)

# Check product consistency
check(
    (
        matched_returns["product_id_return"]
        == matched_returns["product_id_sale"]
    ).all(),
    "Return product matches original sale"
)

# Check returned quantity against original quantity
check(
    (
        matched_returns["returned_quantity"]
        <= matched_returns["quantity"]
    ).all(),
    "Returned quantity does not exceed purchased quantity"
)

# ==========================================
# 8. REFUND AMOUNT VALIDATION
# ==========================================

expected_refunds = (
    (
        matched_returns["gross_sales"]
        - matched_returns["discount_amount"]
    )
    * matched_returns["returned_quantity"]
    / matched_returns["quantity"]
).round(2)

refund_difference = (
    matched_returns["refund_amount"]
    - expected_refunds
).abs()

max_refund_difference = refund_difference.round(2).max()

check(
    max_refund_difference <= 0.01,
    "Refund calculations are correct",
    f"Maximum difference: ₱{max_refund_difference:.2f}"
)

check(
    (df_returns["refund_amount"] >= 0).all(),
    "Refund amounts are non-negative"
)

check(
    df_returns["refund_amount"].notna().all(),
    "Refund amounts are complete"
)


# ==========================================
# 9. RETURN DATE VALIDATION
# ==========================================

# Prepare a date lookup for both return dates
# and original sale dates
date_lookup = df_dates[
    ["date_id", "full_date"]
].copy()

# Match return date
date_check = matched_returns.merge(
    date_lookup.rename(
        columns={
            "date_id": "return_date_id",
            "full_date": "return_date"
        }
    ),
    left_on="date_id_return",
    right_on="return_date_id",
    how="left"
)

# Match original sale date
date_check = date_check.merge(
    date_lookup.rename(
        columns={
            "date_id": "original_date_id",
            "full_date": "original_sale_date"
        }
    ),
    left_on="date_id_sale",
    right_on="original_date_id",
    how="left"
)

check(
    date_check["return_date"].notna().all(),
    "Return dates have valid calendar records"
)

check(
    (
        date_check["return_date"]
        > date_check["original_sale_date"]
    ).all(),
    "Return dates occur after original sales"
)

check(
    (
        date_check["return_date"]
        <= pd.Timestamp(config.END_DATE)
    ).all(),
    "Return dates do not exceed dataset coverage"
)

# ==========================================
# 10. VALIDATION SUMMARY
# ==========================================

print("\n" + "=" * 45)
print("RETURNS DATA VALIDATION SUMMARY")
print("=" * 45)

print(f"Total checks: {total_checks}")
print(f"Passed: {passed_checks}")
print(f"Failed: {failed_checks}")

print("\nReturn records:", f"{len(df_returns):,}")
print(
    "Returned units:",
    f"{df_returns['returned_quantity'].sum():,}"
)
print(
    "Total refunds:",
    f"₱{df_returns['refund_amount'].sum():,.2f}"
)

if failed_checks == 0:
    print("\nALL RETURNS DATA VALIDATIONS PASSED!")
else:
    print("\nVALIDATION FAILED. REVIEW THE FAILED CHECKS.")
