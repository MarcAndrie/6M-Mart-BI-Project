import pandas as pd
import numpy as np
import config

# ==========================================
# 1. LOAD DATASETS
# ==========================================

df_inventory = pd.read_csv(
    config.RAW_DATA_DIR / "fact_inventory.csv"
)

df_products = pd.read_csv(
    config.RAW_DATA_DIR / "dim_products.csv"
)

df_branches = pd.read_csv(
    config.RAW_DATA_DIR / "dim_branches.csv"
)

df_dates = pd.read_csv(
    config.RAW_DATA_DIR / "dim_date.csv"
)

# ==========================================
# 2. VALIDATION SETUP
# ==========================================

total_checks = 0
passed_checks = 0
failed_checks = 0


def check(condition, description, details=""):
    global total_checks, passed_checks, failed_checks

    total_checks += 1

    if condition:
        passed_checks += 1
        print(f"[PASS] {description}")
    else:
        failed_checks += 1
        print(f"[FAIL] {description}")

    if details:
        print(f"       {details}")


print("INVENTORY DATA VALIDATION STARTED")
print("=" * 45)


# ==========================================
# 3. STRUCTURE VALIDATION
# ==========================================

expected_columns = [
    "inventory_id",
    "date_id",
    "branch_id",
    "product_id",
    "quantity_on_hand",
    "reorder_level"
]

check(
    len(df_inventory) > 0,
    "Inventory dataset is not empty"
)

check(
    len(df_inventory) == 101760,
    "Inventory record count",
    f"Found {len(df_inventory):,} records"
)

check(
    df_inventory.columns.tolist() == expected_columns,
    "Inventory dataset has the correct columns"
)

check(
    len(df_inventory.columns) == 6,
    "Inventory dataset has 6 columns"
)


# ==========================================
# 4. ID VALIDATION
# ==========================================

check(
    df_inventory["inventory_id"].is_unique,
    "Inventory ID uniqueness"
)

check(
    df_inventory["inventory_id"].notna().all(),
    "Inventory ID completeness"
)


# ==========================================
# 5. MISSING VALUE VALIDATION
# ==========================================

missing_values = df_inventory.isna().sum().sum()

check(
    missing_values == 0,
    "Required fields have no missing values",
    f"Missing values found: {missing_values}"
)


# ==========================================
# 6. FOREIGN KEY VALIDATION
# ==========================================

check(
    df_inventory["date_id"].isin(
        df_dates["date_id"]
    ).all(),
    "Date foreign keys"
)

check(
    df_inventory["branch_id"].isin(
        df_branches["branch_id"]
    ).all(),
    "Branch foreign keys"
)

check(
    df_inventory["product_id"].isin(
        df_products["product_id"]
    ).all(),
    "Product foreign keys"
)


# ==========================================
# 7. INVENTORY QUANTITY VALIDATION
# ==========================================

check(
    (df_inventory["quantity_on_hand"] >= 0).all(),
    "Inventory quantities are non-negative"
)

check(
    (
        df_inventory["quantity_on_hand"] % 1 == 0
    ).all(),
    "Inventory quantities are whole numbers"
)

check(
    (df_inventory["reorder_level"] > 0).all(),
    "Reorder levels are positive"
)

check(
    (
        df_inventory["reorder_level"] % 1 == 0
    ).all(),
    "Reorder levels are whole numbers"
)


# ==========================================
# 8. SNAPSHOT COMPLETENESS
# ==========================================

expected_snapshots = 106
expected_combinations = (
    len(df_branches) * len(df_products)
)

snapshot_counts = (
    df_inventory
    .groupby("date_id")
    .size()
)

check(
    df_inventory["date_id"].nunique()
    == expected_snapshots,
    "All weekly snapshot dates are present",
    f"Found {df_inventory['date_id'].nunique()} dates"
)

check(
    (snapshot_counts == expected_combinations).all(),
    "Every snapshot has all branch-product combinations",
    f"Expected {expected_combinations} records per snapshot"
)


# ==========================================
# 9. COMPOSITE KEY VALIDATION
# ==========================================

duplicate_combinations = df_inventory.duplicated(
    subset=["date_id", "branch_id", "product_id"]
).sum()

check(
    duplicate_combinations == 0,
    "No duplicate date-branch-product combinations",
    f"Duplicates found: {duplicate_combinations}"
)


# ==========================================
# 10. STOCK SCENARIO VALIDATION
# ==========================================

br003_stockouts = df_inventory[
    (df_inventory["branch_id"] == "BR003")
    & (df_inventory["quantity_on_hand"] == 0)
]

check(
    len(br003_stockouts) > 0,
    "BR003 stockout scenario is present",
    f"Stockout records: {len(br003_stockouts):,}"
)

br006_overstock = df_inventory[
    (df_inventory["branch_id"] == "BR006")
    & (
        df_inventory["quantity_on_hand"]
        >= df_inventory["reorder_level"] * 4
    )
]

check(
    len(br006_overstock) > 0,
    "BR006 overstock scenario is present",
    f"Overstock records: {len(br006_overstock):,}"
)


# ==========================================
# 11. VALIDATION SUMMARY
# ==========================================

print("\n" + "=" * 45)
print("INVENTORY DATA VALIDATION SUMMARY")
print("=" * 45)

print(f"Total checks: {total_checks}")
print(f"Passed: {passed_checks}")
print(f"Failed: {failed_checks}")

print(f"\nInventory records: {len(df_inventory):,}")
print(
    "Stockout records:",
    (df_inventory["quantity_on_hand"] == 0).sum()
)

print(
    "Low-stock records:",
    (
        (df_inventory["quantity_on_hand"] > 0)
        & (
            df_inventory["quantity_on_hand"]
            < df_inventory["reorder_level"]
        )
    ).sum()
)

print(
    "Normal-stock records:",
    (
        df_inventory["quantity_on_hand"]
        >= df_inventory["reorder_level"]
    ).sum()
)

if failed_checks == 0:
    print("\nALL INVENTORY DATA VALIDATIONS PASSED!")
else:
    print("\nINVENTORY DATA VALIDATION FAILED!")