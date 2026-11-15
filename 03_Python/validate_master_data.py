
import pandas as pd
import config

# ==========================================
# 1. LOAD MASTER DATASETS
# ==========================================

branches = pd.read_csv(config.RAW_DATA_DIR / "dim_branches.csv")
suppliers = pd.read_csv(config.RAW_DATA_DIR / "dim_suppliers.csv")
products = pd.read_csv(config.RAW_DATA_DIR / "dim_products.csv")
promotions = pd.read_csv(config.RAW_DATA_DIR / "dim_promotions.csv")
dates = pd.read_csv(config.RAW_DATA_DIR / "dim_date.csv")

# ==========================================
# 2. VALIDATE RECORD COUNTS
# ==========================================

print("MASTER DATA VALIDATION")
print("=" * 45)

expected_counts = {
    "Branches": (branches, 8),
    "Suppliers": (suppliers, 15),
    "Products": (products, 120),
    "Promotions": (promotions, 15),
    "Dates": (dates, 731)
}

for name, (df, expected) in expected_counts.items():
    actual = len(df)
    status = "PASS" if actual == expected else "FAIL"

    print(f"{name}: {actual}/{expected} - {status}")

# ==========================================
# 3. CHECK PRIMARY KEY UNIQUENESS
# ==========================================

primary_keys = {
    "Branches": (branches, "branch_id"),
    "Suppliers": (suppliers, "supplier_id"),
    "Products": (products, "product_id"),
    "Promotions": (promotions, "promotion_id"),
    "Dates": (dates, "date_id")
}

print("\nPRIMARY KEY VALIDATION")
print("=" * 45)

for name, (df, column) in primary_keys.items():
    passed = df[column].is_unique
    status = "PASS" if passed else "FAIL"

    print(f"{name} - {column}: {status}")

# ==========================================
# 4. CHECK MISSING VALUES
# ==========================================

print("\nMISSING VALUE VALIDATION")
print("=" * 45)

for name, df in [
    ("Branches", branches),
    ("Suppliers", suppliers),
    ("Products", products),
    ("Promotions", promotions),
    ("Dates", dates)
]:
    missing = df.isnull().sum().sum()
    status = "PASS" if missing == 0 else "FAIL"

    print(f"{name}: {missing} missing values - {status}")

# ==========================================
# 5. CHECK PRODUCT-SUPPLIER RELATIONSHIP
# ==========================================

valid_suppliers = suppliers["supplier_id"].tolist()

invalid_suppliers = products[
    ~products["supplier_id"].isin(valid_suppliers)
]

print("\nFOREIGN KEY VALIDATION")
print("=" * 45)

print(
    "Product-Supplier Relationship:",
    "PASS" if invalid_suppliers.empty else "FAIL"
)

# ==========================================
# 6. CHECK PRODUCT PRICES AND COSTS
# ==========================================

valid_prices = (
    (products["selling_price"] > 0) &
    (products["unit_cost"] > 0) &
    (products["unit_cost"] < products["selling_price"])
)

print("\nPRODUCT FINANCIAL VALIDATION")
print("=" * 45)

print(
    "Selling Price and Unit Cost:",
    "PASS" if valid_prices.all() else "FAIL"
)

# ==========================================
# 7. CHECK DATE DIMENSION
# ==========================================

dates["full_date"] = pd.to_datetime(dates["full_date"])

expected_dates = pd.date_range(
    start=config.START_DATE,
    end=config.END_DATE,
    freq="D"
)

valid_calendar = (
    len(dates) == len(expected_dates)
    and dates["full_date"].is_unique
    and dates["full_date"].sort_values().reset_index(drop=True).equals(
        pd.Series(expected_dates, name="full_date")
    )
)

print("\nDATE VALIDATION")
print("=" * 45)

print(
    "Complete Daily Calendar:",
    "PASS" if valid_calendar else "FAIL"
)

# ==========================================
# 8. CHECK PROMOTION DATE LOGIC
# ==========================================

promotions["start_date"] = pd.to_datetime(
    promotions["start_date"]
)

promotions["end_date"] = pd.to_datetime(
    promotions["end_date"]
)

valid_promotions = (
    promotions["start_date"] <= promotions["end_date"]
).all()

print("\nPROMOTION VALIDATION")
print("=" * 45)

print(
    "Promotion Date Ranges:",
    "PASS" if valid_promotions else "FAIL"
)

print("\nMASTER DATA VALIDATION COMPLETE!")
