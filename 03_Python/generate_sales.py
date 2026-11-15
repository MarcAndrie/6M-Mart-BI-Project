
import pandas as pd
import numpy as np
import config

# ==========================================
# 1. INITIALIZE RANDOM GENERATOR
# ==========================================

rng = np.random.default_rng(config.RANDOM_SEED)

# ==========================================
# 2. LOAD MASTER DATASETS
# ==========================================

df_products = pd.read_csv(
    config.RAW_DATA_DIR / "dim_products.csv"
)

df_branches = pd.read_csv(
    config.RAW_DATA_DIR / "dim_branches.csv"
)

df_dates = pd.read_csv(
    config.RAW_DATA_DIR / "dim_date.csv"
)

df_promotions = pd.read_csv(
    config.RAW_DATA_DIR / "dim_promotions.csv"
)

# ==========================================
# 3. PREPARE DATE COLUMNS
# ==========================================

df_dates["full_date"] = pd.to_datetime(
    df_dates["full_date"]
)

df_promotions["start_date"] = pd.to_datetime(
    df_promotions["start_date"]
)

df_promotions["end_date"] = pd.to_datetime(
    df_promotions["end_date"]
)

# ==========================================
# 4. DISPLAY LOADED DATA SUMMARY
# ==========================================

print("SALES GENERATOR INITIALIZED")
print("=" * 40)

print(f"Products loaded: {len(df_products)}")
print(f"Branches loaded: {len(df_branches)}")
print(f"Calendar dates loaded: {len(df_dates)}")
print(f"Promotions loaded: {len(df_promotions)}")

print("\nSales line target:", config.SALES_LINE_COUNT)
print("Random seed:", config.RANDOM_SEED)

print("\nAll master datasets loaded successfully!")

# ==========================================
# 5. GENERATE TRANSACTION STRUCTURE
# ==========================================

# Generate a random number of product lines per transaction
# Each transaction will contain 1 to 5 sales lines

transaction_line_counts = []

total_lines = 0

while total_lines < config.SALES_LINE_COUNT:

    line_count = rng.integers(1, 6)

    transaction_line_counts.append(line_count)

    total_lines += line_count

# Trim the final transaction if it exceeds the target
if total_lines > config.SALES_LINE_COUNT:

    excess = total_lines - config.SALES_LINE_COUNT

    transaction_line_counts[-1] -= excess

# Generate unique transaction IDs
num_transactions = len(transaction_line_counts)

transaction_ids = [
    f"TXN{i:07d}"
    for i in range(1, num_transactions + 1)
]

print("\nTRANSACTION STRUCTURE GENERATED")
print("=" * 40)

print(f"Total sales lines: {sum(transaction_line_counts):,}")
print(f"Total transactions: {num_transactions:,}")
print(f"Average lines per transaction: {np.mean(transaction_line_counts):.2f}")
print(f"Minimum lines per transaction: {min(transaction_line_counts)}")
print(f"Maximum lines per transaction: {max(transaction_line_counts)}")


# ==========================================
# 6. ASSIGN DATES AND BRANCHES
# ==========================================

# Create seasonal weights for each month
monthly_weights = {
    1: 0.90,
    2: 0.90,
    3: 1.00,
    4: 0.95,
    5: 1.00,
    6: 0.95,
    7: 0.95,
    8: 0.95,
    9: 1.00,
    10: 1.00,
    11: 1.15,
    12: 1.35
}

# Assign a weight to every calendar date
date_weights = df_dates["month"].map(monthly_weights).to_numpy()

# Normalize weights so they can be used as probabilities
date_probabilities = date_weights / date_weights.sum()

# Randomly assign a date to every transaction
date_indices = rng.choice(
    len(df_dates),
    size=num_transactions,
    p=date_probabilities
)

selected_dates = df_dates.iloc[date_indices].reset_index(drop=True)

# Define gradual quarterly branch trends
br003_shares = {
    1: 0.140,
    2: 0.135,
    3: 0.130,
    4: 0.125,
    5: 0.120,
    6: 0.115,
    7: 0.110,
    8: 0.105
}

br006_shares = {
    1: 0.110,
    2: 0.115,
    3: 0.120,
    4: 0.125,
    5: 0.130,
    6: 0.135,
    7: 0.140,
    8: 0.145
}

# Assign a branch based on each transaction's quarter
branch_ids = df_branches["branch_id"].to_numpy()

selected_branches = []

for transaction_date in selected_dates["full_date"]:

    quarter = ((transaction_date.month - 1) // 3) + 1

    quarter_number = (
        (transaction_date.year - 2024) * 4
    ) + quarter

    br003 = br003_shares[quarter_number]
    br006 = br006_shares[quarter_number]

    # Distribute the remaining probability equally
    # among the other six branches
    other_share = (1 - br003 - br006) / 6

    branch_probabilities = {
        "BR001": other_share,
        "BR002": other_share,
        "BR003": br003,
        "BR004": other_share,
        "BR005": other_share,
        "BR006": br006,
        "BR007": other_share,
        "BR008": other_share
    }

    probabilities = [
        branch_probabilities[branch_id]
        for branch_id in branch_ids
    ]

    selected_branches.append(
        rng.choice(branch_ids, p=probabilities)
    )

# Create transaction-level dataset
transaction_df = pd.DataFrame({
    "transaction_id": transaction_ids,
    "date_id": selected_dates["date_id"],
    "transaction_date": selected_dates["full_date"],
    "branch_id": selected_branches,
    "line_count": transaction_line_counts
})

print("\nTRANSACTION DATES AND BRANCHES ASSIGNED")
print("=" * 40)

print("Transactions:", len(transaction_df))
print("Unique dates:", transaction_df["transaction_date"].nunique())
print("Unique branches:", transaction_df["branch_id"].nunique())

print("\nTransactions by year:")
print(
    transaction_df["transaction_date"]
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nTransactions by month:")
print(
    transaction_df["transaction_date"]
    .dt.month
    .value_counts()
    .sort_index()
)

print("\nTransactions by branch:")
print(
    transaction_df["branch_id"]
    .value_counts()
    .sort_index()
)

print("\nQuarterly branch distribution:")
print(
    transaction_df.assign(
        quarter=(
            (transaction_df["transaction_date"].dt.month - 1) // 3
        ) + 1,
        year=transaction_df["transaction_date"].dt.year
    )
    .groupby(["year", "quarter", "branch_id"])
    .size()
    .unstack(fill_value=0)
)


# ==========================================
# 7. EXPAND TRANSACTIONS INTO SALES LINES
# ==========================================

sales_df = (
    transaction_df
    .loc[transaction_df.index.repeat(transaction_df["line_count"])]
    .reset_index(drop=True)
)

# Generate unique sales line IDs
sales_df["sales_line_id"] = [
    f"SL{i:07d}"
    for i in range(1, len(sales_df) + 1)
]

# Remove the temporary line_count column
sales_df = sales_df.drop(columns=["line_count"])

# Arrange columns
sales_df = sales_df[
    [
        "sales_line_id",
        "transaction_id",
        "date_id",
        "transaction_date",
        "branch_id"
    ]
]

print("\nSALES LINES EXPANDED")
print("=" * 40)

print(f"Total sales lines: {len(sales_df):,}")
print(f"Unique sales line IDs: {sales_df['sales_line_id'].nunique():,}")
print(f"Unique transactions: {sales_df['transaction_id'].nunique():,}")

print("\nSample sales lines:")
print(sales_df.head(10).to_string(index=False))

# ==========================================
# 8. ASSIGN PRODUCTS TO SALES LINES
# ==========================================

# Define category-level demand weights
category_weights = {
    "Groceries": 0.30,
    "Beverages": 0.18,
    "Dairy": 0.15,
    "Fresh Produce": 0.15,
    "Personal Care": 0.11,
    "Household Essentials": 0.11
}

# Assign each product a category weight
df_products["category_weight"] = (
    df_products["category"]
    .map(category_weights)
)

# Add individual product popularity variation
product_popularity = rng.lognormal(
    mean=0,
    sigma=0.7,
    size=len(df_products)
)

# Calculate final product selection weights
product_weights = (
    df_products["category_weight"].to_numpy()
    * product_popularity
)

# Convert weights into probabilities
product_probabilities = (
    product_weights / product_weights.sum()
)

# Generate product selections transaction by transaction
selected_product_ids = []

for line_count in transaction_line_counts:

    products_in_transaction = rng.choice(
        df_products["product_id"].to_numpy(),
        size=line_count,
        replace=False,
        p=product_probabilities
    )

    selected_product_ids.extend(products_in_transaction)

# Assign product IDs to sales lines
sales_df["product_id"] = selected_product_ids

# Validate product assignments
print("\nPRODUCTS ASSIGNED")
print("=" * 40)

print(f"Sales lines: {len(sales_df):,}")
print(f"Unique products sold: {sales_df['product_id'].nunique()}")

print("\nSales lines by category:")

category_summary = (
    sales_df
    .merge(
        df_products[["product_id", "category"]],
        on="product_id",
        how="left"
    )
    ["category"]
    .value_counts()
)

print(category_summary.to_string())

print("\nTop 10 most frequently selected products:")

print(
    sales_df["product_id"]
    .value_counts()
    .head(10)
    .to_string()
)

# ==========================================
# 9. ASSIGN QUANTITIES AND PRICES
# ==========================================

# Generate quantities between 1 and 5 units
sales_df["quantity"] = rng.choice(
    [1, 2, 3, 4, 5],
    size=len(sales_df),
    p=[0.40, 0.30, 0.17, 0.09, 0.04]
)

# Attach product prices and costs
sales_df = sales_df.merge(
    df_products[
        ["product_id", "selling_price", "unit_cost"]
    ],
    on="product_id",
    how="left"
)

# Preserve historical prices and costs
sales_df = sales_df.rename(
    columns={"selling_price": "unit_price"}
)

# Calculate gross sales per line
sales_df["gross_sales"] = (
    sales_df["quantity"] * sales_df["unit_price"]
).round(2)

print("\nQUANTITIES AND PRICES ASSIGNED")
print("=" * 40)

print(f"Total sales lines: {len(sales_df):,}")
print(f"Total units sold: {sales_df['quantity'].sum():,}")

print("\nQuantity distribution:")
print(
    sales_df["quantity"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nSales value summary:")
print(
    sales_df[
        ["unit_price", "unit_cost", "gross_sales"]
    ].describe().round(2)
)

print("\nSample sales records:")
print(
    sales_df[
        [
            "sales_line_id",
            "transaction_id",
            "product_id",
            "quantity",
            "unit_price",
            "unit_cost",
            "gross_sales"
        ]
    ].head(10).to_string(index=False)
)

# ==========================================
# 10. ASSIGN PROMOTIONS TO SALES LINES
# ==========================================

# Build a calendar of active promotions
promotion_calendar = {}

for date in df_dates["full_date"]:

    active_promotions = df_promotions.loc[
        (df_promotions["start_date"] <= date)
        & (df_promotions["end_date"] >= date),
        "promotion_id"
    ].to_numpy()

    promotion_calendar[date] = active_promotions


# Assign promotions to eligible sales lines
# 70% chance of receiving a promotion on eligible dates

selected_promotion_ids = []

for sale_date in sales_df["transaction_date"]:

    eligible_promotions = promotion_calendar[sale_date]

    if len(eligible_promotions) > 0 and rng.random() < 0.70:

        selected_promotion = rng.choice(eligible_promotions)

    else:

        selected_promotion = None

    selected_promotion_ids.append(selected_promotion)


sales_df["promotion_id"] = selected_promotion_ids


# Attach promotion details
sales_df = sales_df.merge(
    df_promotions[
        [
            "promotion_id",
            "promotion_name",
            "discount_type",
            "discount_value"
        ]
    ],
    on="promotion_id",
    how="left"
)


# Calculate discounts
raw_discount = np.where(
    sales_df["discount_type"] == "Percentage",

    sales_df["gross_sales"]
    * sales_df["discount_value"] / 100,

    sales_df["quantity"]
    * sales_df["discount_value"]
)

# Replace missing discounts with zero and prevent
# discounts from exceeding the line's gross sales
sales_df["discount_amount"] = np.minimum(
    np.nan_to_num(raw_discount, nan=0.0),
    sales_df["gross_sales"]
).round(2)


print("\nPROMOTIONS AND DISCOUNTS ASSIGNED")
print("=" * 40)

promoted_lines = sales_df["promotion_id"].notna().sum()

print(f"Total sales lines: {len(sales_df):,}")
print(f"Promoted sales lines: {promoted_lines:,}")
print(f"Non-promoted sales lines: {len(sales_df) - promoted_lines:,}")

print(f"\nTotal discount amount: PHP {sales_df['discount_amount'].sum():,.2f}")

print("\nSales lines by promotion:")
print(
    sales_df.groupby(
        ["promotion_id", "promotion_name"],
        dropna=True
    )
    .size()
    .to_string()
)

print("\nDiscount summary:")
print(
    sales_df.groupby("discount_type", dropna=False)["discount_amount"]
    .agg(["count", "sum", "mean"])
    .round(2)
    .to_string()
)

print("\nSample promotion records:")
print(
    sales_df[
        [
            "sales_line_id",
            "transaction_date",
            "product_id",
            "quantity",
            "gross_sales",
            "promotion_id",
            "discount_type",
            "discount_amount"
        ]
    ].head(15).to_string(index=False)
)

# ==========================================
# 11. CALCULATE SALES AND PROFITABILITY
# ==========================================

# Net sales before returns
sales_df["net_sales"] = (
    sales_df["gross_sales"] - sales_df["discount_amount"]
).round(2)

# Cost of goods sold before returns
sales_df["cogs"] = (
    sales_df["quantity"] * sales_df["unit_cost"]
).round(2)

# Gross profit before returns
sales_df["gross_profit"] = (
    sales_df["net_sales"] - sales_df["cogs"]
).round(2)

# Gross profit margin
sales_df["gross_profit_margin"] = np.where(
    sales_df["net_sales"] > 0,
    sales_df["gross_profit"] / sales_df["net_sales"] * 100,
    0
).round(2)


print("\nSALES AND PROFITABILITY CALCULATED")
print("=" * 40)

print(f"Gross Sales: PHP {sales_df['gross_sales'].sum():,.2f}")
print(f"Discounts: PHP {sales_df['discount_amount'].sum():,.2f}")
print(f"Net Sales Before Returns: PHP {sales_df['net_sales'].sum():,.2f}")
print(f"COGS Before Returns: PHP {sales_df['cogs'].sum():,.2f}")
print(f"Gross Profit Before Returns: PHP {sales_df['gross_profit'].sum():,.2f}")

overall_margin = (
    sales_df["gross_profit"].sum()
    / sales_df["net_sales"].sum()
    * 100
)

print(f"Gross Profit Margin: {overall_margin:.2f}%")

print("\nProfitability Summary:")
print(
    sales_df[
        [
            "gross_sales",
            "discount_amount",
            "net_sales",
            "cogs",
            "gross_profit",
            "gross_profit_margin"
        ]
    ].describe().round(2)
)

print("\nSample financial records:")
print(
    sales_df[
        [
            "sales_line_id",
            "gross_sales",
            "discount_amount",
            "net_sales",
            "cogs",
            "gross_profit",
            "gross_profit_margin"
        ]
    ].head(10).to_string(index=False)
)

# ==========================================
# 12. FINALIZE AND SAVE SALES FACT DATASET
# ==========================================

# Select final fact table columns
fact_sales = sales_df[
    [
        "sales_line_id",
        "transaction_id",
        "date_id",
        "branch_id",
        "product_id",
        "promotion_id",
        "quantity",
        "unit_price",
        "unit_cost",
        "gross_sales",
        "discount_amount"
    ]
].copy()

# Save dataset
output_path = config.RAW_DATA_DIR / "fact_sales.csv"

fact_sales.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\nFACT SALES DATASET SAVED")
print("=" * 40)

print(f"Records: {len(fact_sales):,}")
print(f"Columns: {len(fact_sales.columns)}")
print(f"File: {output_path}")

print("\nFinal columns:")
print(fact_sales.columns.tolist())

print("\nDataset preview:")
print(fact_sales.head(5).to_string(index=False))