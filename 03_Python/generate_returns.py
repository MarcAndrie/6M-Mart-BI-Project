
import pandas as pd
import numpy as np
import config

# Use a separate random generator for returns
rng = np.random.default_rng(config.RANDOM_SEED + 1)

# Load sales fact table
df_sales = pd.read_csv(
    config.RAW_DATA_DIR / "fact_sales.csv"
)

# Load date dimension
df_dates = pd.read_csv(
    config.RAW_DATA_DIR / "dim_date.csv"
)

# Convert date columns
df_dates["full_date"] = pd.to_datetime(
    df_dates["full_date"]
)

# Attach the original transaction date to each sales line
df_sales = df_sales.merge(
    df_dates[["date_id", "full_date"]],
    on="date_id",
    how="left"
)

print("RETURNS GENERATOR INITIALIZED")
print("=" * 40)

print(f"Sales lines loaded: {len(df_sales):,}")
print(f"Calendar dates loaded: {len(df_dates):,}")
print(f"Configured return rate: {config.RETURN_RATE:.0%}")

print("\nSales dataset preview:")
print(df_sales.head().to_string(index=False))


# ==========================================
# 2. SELECT SALES LINES FOR RETURNS
# ==========================================

# A return must occur after the original sale.
# Exclude sales on the final calendar date because
# there is no later date available in our dataset.

eligible_sales = df_sales[
    df_sales["full_date"] < pd.Timestamp(config.END_DATE)
].copy()

# Randomly select sales lines using the configured return rate
return_mask = (
    rng.random(len(eligible_sales)) < config.RETURN_RATE
)

returned_sales = (
    eligible_sales.loc[return_mask]
    .copy()
    .reset_index(drop=True)
)

print("\nSALES LINES SELECTED FOR RETURNS")
print("=" * 40)

print(f"Eligible sales lines: {len(eligible_sales):,}")
print(f"Selected return events: {len(returned_sales):,}")

actual_return_rate = (
    len(returned_sales) / len(eligible_sales) * 100
)

print(f"Actual return rate: {actual_return_rate:.2f}%")

print("\nSelected sales preview:")
print(
    returned_sales[
        [
            "sales_line_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_amount",
            "full_date"
        ]
    ].head(10).to_string(index=False)
)


# ==========================================
# 3. GENERATE RETURN DATES
# ==========================================

# Calculate the maximum available days between
# each original sale and the end of our dataset
dataset_end = pd.Timestamp(config.END_DATE)

days_remaining = (
    dataset_end - returned_sales["full_date"]
).dt.days.to_numpy()

# Generate a random return period between 1 and
# 30 days, without exceeding the dataset end date
return_days = np.array([
    rng.integers(1, min(30, days_left) + 1)
    for days_left in days_remaining
])

# Calculate the actual return dates
returned_sales["return_date"] = (
    returned_sales["full_date"]
    + pd.to_timedelta(return_days, unit="D")
)

# Map return dates to date IDs
date_id_map = (
    df_dates.set_index("full_date")["date_id"]
    .to_dict()
)

returned_sales["return_date_id"] = (
    returned_sales["return_date"].map(date_id_map)
)

print("\nRETURN DATES GENERATED")
print("=" * 40)

print("Return events:", len(returned_sales))
print(
    "Earliest return date:",
    returned_sales["return_date"].min().date()
)
print(
    "Latest return date:",
    returned_sales["return_date"].max().date()
)

print("\nReturn period distribution:")
print(
    pd.Series(return_days)
    .describe()
    .round(2)
)

print("\nReturn date preview:")
print(
    returned_sales[
        [
            "sales_line_id",
            "full_date",
            "return_date",
            "return_date_id"
        ]
    ].head(10).to_string(index=False)
)

# Basic date integrity checks
assert (
    returned_sales["return_date"] > returned_sales["full_date"]
).all(), "A return date is not after its original sale date."

assert (
    returned_sales["return_date"] <= dataset_end
).all(), "A return date exceeds the dataset end date."

assert (
    returned_sales["return_date_id"].notna()
).all(), "Some return dates have no matching date ID."

print("\nAll return date checks passed!")


# ==========================================
# 4. GENERATE RETURNED QUANTITIES
# ==========================================

# Generate a random returned quantity between
# 1 and the original quantity purchased
returned_sales["returned_quantity"] = [
    rng.integers(1, original_quantity + 1)
    for original_quantity in returned_sales["quantity"]
]

print("\nRETURNED QUANTITIES GENERATED")
print("=" * 40)

print(
    "Total returned units:",
    returned_sales["returned_quantity"].sum()
)

print("\nReturned quantity distribution:")
print(
    returned_sales["returned_quantity"]
    .value_counts()
    .sort_index()
)

print("\nOriginal vs. returned quantities:")
print(
    returned_sales[
        [
            "sales_line_id",
            "quantity",
            "returned_quantity"
        ]
    ].head(10).to_string(index=False)
)

# Validate returned quantities
assert (
    returned_sales["returned_quantity"] >= 1
).all(), "Found a returned quantity below 1."

assert (
    returned_sales["returned_quantity"]
    <= returned_sales["quantity"]
).all(), "Returned quantity exceeds original quantity."

print("\nAll returned quantity checks passed!")


# ==========================================
# 5. CALCULATE REFUND AMOUNTS
# ==========================================

# Calculate the original net sales after discounts
returned_sales["original_net_sales"] = (
    returned_sales["gross_sales"]
    - returned_sales["discount_amount"]
).round(2)

# Calculate the proportional refund based on
# the quantity returned
returned_sales["refund_amount"] = (
    returned_sales["original_net_sales"]
    * returned_sales["returned_quantity"]
    / returned_sales["quantity"]
).round(2)

print("\nREFUND AMOUNTS CALCULATED")
print("=" * 40)

print(
    "Total refunds: ₱{:,.2f}".format(
        returned_sales["refund_amount"].sum()
    )
)

print(
    "Average refund: ₱{:,.2f}".format(
        returned_sales["refund_amount"].mean()
    )
)

print("\nRefund preview:")
print(
    returned_sales[
        [
            "sales_line_id",
            "quantity",
            "returned_quantity",
            "gross_sales",
            "discount_amount",
            "original_net_sales",
            "refund_amount"
        ]
    ].head(10).to_string(index=False)
)

# Validate refund amounts
assert (
    returned_sales["refund_amount"] >= 0
).all(), "Found a negative refund amount."

assert (
    returned_sales["refund_amount"]
    <= returned_sales["original_net_sales"] + 0.01
).all(), "Refund exceeds the original net sales."

assert (
    returned_sales["refund_amount"].notna()
).all(), "Found missing refund amounts."

print("\nAll refund calculation checks passed!")


# ==========================================
# 6. FINALIZE AND SAVE RETURNS FACT DATASET
# ==========================================

# Generate unique return IDs
returned_sales["return_id"] = [
    f"RTN{i:07d}"
    for i in range(1, len(returned_sales) + 1)
]

# Build the final fact table
fact_returns = returned_sales[
    [
        "return_id",
        "sales_line_id",
        "return_date_id",
        "branch_id",
        "product_id",
        "returned_quantity",
        "refund_amount"
    ]
].copy()

# Rename return_date_id to date_id
fact_returns = fact_returns.rename(
    columns={"return_date_id": "date_id"}
)

# Save dataset
output_path = config.RAW_DATA_DIR / "fact_returns.csv"

fact_returns.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\nFACT RETURNS DATASET SAVED")
print("=" * 40)

print(f"Records: {len(fact_returns):,}")
print(f"Columns: {len(fact_returns.columns)}")
print(f"File: {output_path}")

print("\nFinal columns:")
print(fact_returns.columns.tolist())

print("\nDataset preview:")
print(fact_returns.head(10).to_string(index=False))

print("\nReturn summary:")
print(
    f"Total returned units: "
    f"{fact_returns['returned_quantity'].sum():,}"
)

print(
    f"Total refunds: "
    f"₱{fact_returns['refund_amount'].sum():,.2f}"
)

