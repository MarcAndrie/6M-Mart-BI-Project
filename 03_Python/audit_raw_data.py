
import pandas as pd
import config

# ==========================================
# 1. DEFINE DATASETS
# ==========================================

datasets = {
    "dim_branches": "dim_branches.csv",
    "dim_suppliers": "dim_suppliers.csv",
    "dim_products": "dim_products.csv",
    "dim_promotions": "dim_promotions.csv",
    "dim_date": "dim_date.csv",
    "fact_sales": "fact_sales.csv",
    "fact_returns": "fact_returns.csv",
    "fact_inventory": "fact_inventory.csv"
}

primary_keys = {
    "dim_branches": ["branch_id"],
    "dim_suppliers": ["supplier_id"],
    "dim_products": ["product_id"],
    "dim_promotions": ["promotion_id"],
    "dim_date": ["date_id"],
    "fact_sales": ["sales_line_id"],
    "fact_returns": ["return_id"],
    "fact_inventory": ["inventory_id"]
}

# Columns allowed to contain missing values
nullable_columns = {
    "fact_sales": ["promotion_id"]
}

# ==========================================
# 2. AUDIT EACH DATASET
# ==========================================

print("=" * 60)
print("6M MART - RAW DATA QUALITY AUDIT")
print("=" * 60)

audit_summary = []

for dataset_name, filename in datasets.items():

    df = pd.read_csv(config.RAW_DATA_DIR / filename)

    print(f"\n{'=' * 60}")
    print(f"DATASET: {dataset_name.upper()}")
    print("=" * 60)

    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # --------------------------------------
    # COLUMN INFORMATION
    # --------------------------------------

    print("\nCOLUMN DATA TYPES:")
    print(df.dtypes.to_string())

    # --------------------------------------
    # MISSING VALUE VALIDATION
    # --------------------------------------

    missing = df.isna().sum()
    total_missing = int(missing.sum())

    allowed_missing_columns = nullable_columns.get(
        dataset_name, []
    )

    unexpected_missing = missing.drop(
        labels=allowed_missing_columns,
        errors="ignore"
    )

    print("\nMISSING VALUES:")

    if missing.any():
        print(missing[missing > 0].to_string())
    else:
        print("No missing values found")

    print(
        "Expected optional missing values:",
        int(missing[allowed_missing_columns].sum())
        if allowed_missing_columns else 0
    )

    unexpected_missing_total = unexpected_missing.sum()

    print(
        f"Unexpected missing values: {unexpected_missing_total:,}"
    )

    # --------------------------------------
    # DUPLICATE RECORDS
    # --------------------------------------

    duplicate_rows = df.duplicated().sum()

    print("\nDUPLICATE RECORDS:")
    print(f"Exact duplicate rows: {duplicate_rows:,}")

    # --------------------------------------
    # PRIMARY KEY VALIDATION
    # --------------------------------------

    pk_columns = primary_keys[dataset_name]

    duplicate_pk = df.duplicated(
        subset=pk_columns
    ).sum()

    missing_pk = df[pk_columns].isna().sum().sum()

    print("\nPRIMARY KEY CHECK:")
    print(f"Duplicate primary keys: {duplicate_pk:,}")
    print(f"Missing primary key values: {missing_pk:,}")

    # --------------------------------------
    # NUMERIC SUMMARY
    # --------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        print("\nNUMERIC SUMMARY:")
        print(
            df[numeric_columns]
            .describe()
            .round(2)
            .to_string()
        )

    # --------------------------------------
    # DATE SUMMARY
    # --------------------------------------

    date_columns = [
        col for col in df.columns
        if col in ["full_date", "start_date", "end_date"]
    ]

    for column in date_columns:

        parsed_dates = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        print(f"\nDATE RANGE: {column}")
        print(f"Earliest: {parsed_dates.min()}")
        print(f"Latest: {parsed_dates.max()}")
        print(
            f"Unparseable dates: {parsed_dates.isna().sum():,}"
        )

    # --------------------------------------
    # SAVE AUDIT SUMMARY
    # --------------------------------------

    audit_summary.append({
        "dataset": dataset_name,
        "records": len(df),
        "columns": len(df.columns),
        "missing_values": total_missing,
        "unexpected_missing_values": unexpected_missing_total,
        "duplicate_rows": duplicate_rows,
        "duplicate_primary_keys": duplicate_pk,
        "missing_primary_keys": missing_pk
    })


# ==========================================
# 3. FINAL AUDIT SUMMARY
# ==========================================

df_audit = pd.DataFrame(audit_summary)

print("\n" + "=" * 60)
print("RAW DATA AUDIT SUMMARY")
print("=" * 60)

print(df_audit.to_string(index=False))

print("\nRAW DATA AUDIT COMPLETED!")
