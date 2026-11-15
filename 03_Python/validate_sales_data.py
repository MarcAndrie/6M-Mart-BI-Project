
import pandas as pd
import config

# ==========================================
# 1. LOAD DATASETS
# ==========================================

sales = pd.read_csv(config.RAW_DATA_DIR / "fact_sales.csv")
products = pd.read_csv(config.RAW_DATA_DIR / "dim_products.csv")
branches = pd.read_csv(config.RAW_DATA_DIR / "dim_branches.csv")
dates = pd.read_csv(config.RAW_DATA_DIR / "dim_date.csv")
promotions = pd.read_csv(config.RAW_DATA_DIR / "dim_promotions.csv")

dates["full_date"] = pd.to_datetime(dates["full_date"])
promotions["start_date"] = pd.to_datetime(promotions["start_date"])
promotions["end_date"] = pd.to_datetime(promotions["end_date"])

# ==========================================
# 2. VALIDATION HELPER
# ==========================================

results = []

def check(name, passed, details=""):
    results.append(passed)
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if details:
        print(f"       {details}")

# ==========================================
# 3. RECORD COUNT AND PRIMARY KEY
# ==========================================

check(
    "Sales record count",
    len(sales) == config.SALES_LINE_COUNT,
    f"Found {len(sales):,} records"
)

check(
    "Sales line ID uniqueness",
    sales["sales_line_id"].is_unique
)

check(
    "Sales line ID completeness",
    sales["sales_line_id"].notna().all()
)

# ==========================================
# 4. REQUIRED FIELD COMPLETENESS
# ==========================================

required_columns = [
    "sales_line_id",
    "transaction_id",
    "date_id",
    "branch_id",
    "product_id",
    "quantity",
    "unit_price",
    "unit_cost",
    "gross_sales",
    "discount_amount"
]

missing_values = sales[required_columns].isna().sum()
missing_count = int(missing_values.sum())

check(
    "Required fields have no missing values",
    missing_count == 0,
    f"Missing values found: {missing_count}"
)

# ==========================================
# 5. FOREIGN KEY VALIDATION
# ==========================================

check(
    "Product foreign keys",
    sales["product_id"].isin(products["product_id"]).all()
)

check(
    "Branch foreign keys",
    sales["branch_id"].isin(branches["branch_id"]).all()
)

check(
    "Date foreign keys",
    sales["date_id"].isin(dates["date_id"]).all()
)

valid_promotion_ids = promotions["promotion_id"].tolist()

check(
    "Promotion foreign keys",
    sales["promotion_id"].dropna().isin(valid_promotion_ids).all()
)

# ==========================================
# 6. QUANTITY AND PRICE VALIDATION
# ==========================================

check(
    "Quantity is within 1–5 units",
    sales["quantity"].between(1, 5).all()
)

check(
    "Unit prices are positive",
    (sales["unit_price"] > 0).all()
)

check(
    "Unit costs are positive",
    (sales["unit_cost"] > 0).all()
)

# ==========================================
# 7. FINANCIAL VALIDATION
# ==========================================

expected_gross = (
    sales["quantity"] * sales["unit_price"]
).round(2)

gross_difference = (
    sales["gross_sales"] - expected_gross
).abs()

check(
    "Gross sales calculation",
    (gross_difference <= 0.01).all(),
    f"Maximum difference: ₱{gross_difference.max():.4f}"
)

check(
    "Discounts are non-negative",
    (sales["discount_amount"] >= 0).all()
)

check(
    "Discounts do not exceed gross sales",
    (sales["discount_amount"] <= sales["gross_sales"] + 0.01).all()
)

# Non-promotional lines should have zero discounts
non_promo = sales["promotion_id"].isna()

check(
    "Non-promotional sales have zero discounts",
    (sales.loc[non_promo, "discount_amount"] == 0).all()
)

# ==========================================
# 8. TRANSACTION CONSISTENCY
# ==========================================

duplicate_products = sales.duplicated(
    subset=["transaction_id", "product_id"]
).sum()

check(
    "No duplicate products within a transaction",
    duplicate_products == 0,
    f"Duplicates found: {duplicate_products}"
)

transaction_consistency = sales.groupby("transaction_id").agg(
    date_count=("date_id", "nunique"),
    branch_count=("branch_id", "nunique")
)

check(
    "Each transaction has one date and branch",
    (
        (transaction_consistency["date_count"] == 1)
        & (transaction_consistency["branch_count"] == 1)
    ).all()
)

check(
    "Transaction line count is within 1–5",
    sales.groupby("transaction_id").size().between(1, 5).all()
)

# ==========================================
# 9. PROMOTION DATE VALIDATION
# ==========================================

sales_dates = sales.merge(
    dates[["date_id", "full_date"]],
    on="date_id",
    how="left"
)

promoted_sales = sales_dates[
    sales_dates["promotion_id"].notna()
].merge(
    promotions[["promotion_id", "start_date", "end_date"]],
    on="promotion_id",
    how="left"
)

valid_promotion_dates = (
    (promoted_sales["full_date"] >= promoted_sales["start_date"])
    & (promoted_sales["full_date"] <= promoted_sales["end_date"])
)

check(
    "Promotions used within their active dates",
    valid_promotion_dates.all(),
    f"Promoted lines checked: {len(promoted_sales):,}"
)

# ==========================================
# 10. FINAL VALIDATION SUMMARY
# ==========================================

passed = sum(results)
total = len(results)
failed = total - passed

print("\n" + "=" * 45)
print("SALES DATA VALIDATION SUMMARY")
print("=" * 45)

print(f"Total checks: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print("\nALL SALES DATA VALIDATIONS PASSED!")
else:
    print("\nVALIDATION ISSUES FOUND. REVIEW FAILED CHECKS.")
