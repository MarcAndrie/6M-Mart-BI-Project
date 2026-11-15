import pandas as pd
from pathlib import Path

from config import RAW_DATA_DIR, CLEANED_DATA_DIR


# --------------------------------------
# DATASET CONFIGURATION
# --------------------------------------

datasets = [
    "dim_branches",
    "dim_suppliers",
    "dim_products",
    "dim_promotions",
    "dim_date",
    "fact_sales",
    "fact_returns",
    "fact_inventory"
]


# --------------------------------------
# CREATE CLEANED DATA DIRECTORY
# --------------------------------------

CLEANED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------
# LOAD RAW DATASETS
# --------------------------------------

raw_data = {}

for dataset in datasets:

    file_path = RAW_DATA_DIR / f"{dataset}.csv"

    df = pd.read_csv(file_path)

    raw_data[dataset] = df

    print(
        f"[LOADED] {dataset}: "
        f"{len(df):,} records"
    )


print("\nALL RAW DATASETS LOADED SUCCESSFULLY!")

# --------------------------------------
# DEFINE DATA TYPES
# --------------------------------------

string_columns = {
    "dim_branches": [
        "branch_id", "branch_name", "city",
        "region", "branch_type"
    ],

    "dim_suppliers": [
        "supplier_id", "supplier_name",
        "supplier_category"
    ],

    "dim_products": [
        "product_id", "product_name",
        "category", "supplier_id"
    ],

    "dim_promotions": [
        "promotion_id", "promotion_name",
        "discount_type"
    ],

    "fact_sales": [
        "sales_line_id", "transaction_id",
        "branch_id", "product_id", "promotion_id"
    ],

    "fact_returns": [
        "return_id", "sales_line_id",
        "branch_id", "product_id"
    ],

    "fact_inventory": [
        "inventory_id", "branch_id", "product_id"
    ]
}


date_columns = {
    "dim_promotions": ["start_date", "end_date"],
    "dim_date": ["full_date"]
}


# --------------------------------------
# APPLY DATA TYPES
# --------------------------------------

for dataset, df in raw_data.items():

    # Convert identifier and descriptive columns to strings
    for column in string_columns.get(dataset, []):
        df[column] = df[column].astype("string")

    # Convert actual date columns to datetime
    for column in date_columns.get(dataset, []):
        df[column] = pd.to_datetime(
            df[column],
            errors="raise"
        )

    raw_data[dataset] = df

    print(f"\n[CONVERTED] {dataset}")

    print(df.dtypes.to_string())


print("\nDATA TYPE CONVERSION COMPLETED!")

# --------------------------------------
# DATA QUALITY CHECKS
# --------------------------------------

print("\n" + "=" * 50)
print("CLEANED DATA QUALITY CHECKS")
print("=" * 50)

for dataset, df in raw_data.items():

    print(f"\nDATASET: {dataset.upper()}")

    # Check for empty datasets
    assert not df.empty, f"{dataset} is empty"

    # Check for duplicate rows
    assert not df.duplicated().any(), (
        f"{dataset} contains duplicate rows"
    )

    # Check for missing values in required columns
    allowed_nulls = {
        "fact_sales": ["promotion_id"]
    }

    unexpected_missing = df.drop(
        columns=allowed_nulls.get(dataset, [])
    ).isna().sum().sum()

    assert unexpected_missing == 0, (
        f"{dataset} contains unexpected missing values"
    )

    print("[PASS] Dataset is not empty")
    print("[PASS] No duplicate rows")
    print("[PASS] No unexpected missing values")


# --------------------------------------
# FINANCIAL VALIDATION
# --------------------------------------

sales = raw_data["fact_sales"]
returns = raw_data["fact_returns"]

assert (sales["quantity"] > 0).all()
assert (sales["unit_price"] > 0).all()
assert (sales["unit_cost"] > 0).all()
assert (sales["gross_sales"] >= 0).all()
assert (sales["discount_amount"] >= 0).all()
assert (
    sales["discount_amount"] <= sales["gross_sales"]
).all()

assert (returns["returned_quantity"] > 0).all()
assert (returns["refund_amount"] >= 0).all()

print("\n[PASS] Sales financial values are valid")
print("[PASS] Return financial values are valid")


# --------------------------------------
# INVENTORY VALIDATION
# --------------------------------------

inventory = raw_data["fact_inventory"]

assert (inventory["quantity_on_hand"] >= 0).all()
assert (inventory["reorder_level"] > 0).all()

print("[PASS] Inventory quantities are valid")

print("\nALL CLEANED DATA QUALITY CHECKS PASSED!")

# --------------------------------------
# EXPORT CLEANED DATASETS
# --------------------------------------

print("\n" + "=" * 50)
print("EXPORTING CLEANED DATASETS")
print("=" * 50)

for dataset, df in raw_data.items():

    output_path = CLEANED_DATA_DIR / f"{dataset}.csv"

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d"
    )

    print(
        f"[SAVED] {dataset}.csv "
        f"({len(df):,} records)"
    )


# --------------------------------------
# EXPORT SUMMARY
# --------------------------------------

print("\n" + "=" * 50)
print("CLEANED DATA EXPORT SUMMARY")
print("=" * 50)

total_records = 0

for dataset in datasets:

    file_path = CLEANED_DATA_DIR / f"{dataset}.csv"

    exported_df = pd.read_csv(file_path)

    record_count = len(exported_df)
    total_records += record_count

    print(f"{dataset}: {record_count:,} records")

print("-" * 50)
print(f"Total records exported: {total_records:,}")

print("\nALL CLEANED DATASETS EXPORTED SUCCESSFULLY!")

# --------------------------------------
# RAW VS CLEANED COMPARISON
# --------------------------------------

print("\n" + "=" * 50)
print("RAW VS CLEANED DATA COMPARISON")
print("=" * 50)

for dataset in datasets:

    raw_path = RAW_DATA_DIR / f"{dataset}.csv"
    clean_path = CLEANED_DATA_DIR / f"{dataset}.csv"

    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(clean_path)

    # Compare record counts
    assert len(raw_df) == len(clean_df), (
        f"{dataset}: Record count mismatch"
    )

    # Compare column names and order
    assert list(raw_df.columns) == list(clean_df.columns), (
        f"{dataset}: Column mismatch"
    )

    # Compare actual data values
    pd.testing.assert_frame_equal(
        raw_df,
        clean_df,
        check_dtype=False,
        check_exact=False,
        rtol=1e-10,
        atol=1e-10
    )

    print(f"[PASS] {dataset}: Raw and cleaned data match")


print("\n" + "=" * 50)
print("FINAL DATA PREPARATION RESULT")
print("=" * 50)

print("Datasets compared:", len(datasets))
print("Total records:", sum(
    len(pd.read_csv(RAW_DATA_DIR / f"{d}.csv"))
    for d in datasets
))

print("\nALL RAW AND CLEANED DATASETS MATCH!")