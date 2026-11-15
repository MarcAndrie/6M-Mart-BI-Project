import pandas as pd
import numpy as np
import config

rng = np.random.default_rng(config.RANDOM_SEED + 2)

# ==========================================
# 1. LOAD REQUIRED DATASETS
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

df_sales = pd.read_csv(
    config.RAW_DATA_DIR / "fact_sales.csv"
)

df_dates["full_date"] = pd.to_datetime(
    df_dates["full_date"]
)

print("INVENTORY GENERATOR INITIALIZED")
print("=" * 40)

print(f"Products loaded: {len(df_products):,}")
print(f"Branches loaded: {len(df_branches):,}")
print(f"Calendar dates loaded: {len(df_dates):,}")
print(f"Sales lines loaded: {len(df_sales):,}")

# ==========================================
# 2. GENERATE WEEKLY SNAPSHOT DATES
# ==========================================

start_date = pd.Timestamp(config.START_DATE)
end_date = pd.Timestamp(config.END_DATE)

snapshot_dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="7D"
)

# Include the final date if it isn't already present
if snapshot_dates[-1] != end_date:
    snapshot_dates = snapshot_dates.append(
        pd.DatetimeIndex([end_date])
    )

date_lookup = df_dates.set_index(
    "full_date"
)["date_id"]

snapshot_date_ids = date_lookup.loc[
    snapshot_dates
].to_numpy()

print("\nWEEKLY SNAPSHOT DATES")
print("=" * 40)

print(f"Number of snapshots: {len(snapshot_dates)}")
print(f"First snapshot: {snapshot_dates[0].date()}")
print(f"Last snapshot: {snapshot_dates[-1].date()}")

# ==========================================
# 3. BUILD INVENTORY SNAPSHOT STRUCTURE
# ==========================================

df_snapshots = pd.DataFrame({
    "date_id": snapshot_date_ids,
    "snapshot_date": snapshot_dates
})

df_inventory = (
    df_snapshots[["date_id"]]
    .merge(df_branches[["branch_id"]], how="cross")
    .merge(df_products[["product_id"]], how="cross")
)

print("\nINVENTORY SNAPSHOT STRUCTURE")
print("=" * 40)

print(f"Expected records: {len(snapshot_dates) * len(df_branches) * len(df_products):,}")
print(f"Generated records: {len(df_inventory):,}")

print(f"Unique dates: {df_inventory['date_id'].nunique()}")
print(f"Unique branches: {df_inventory['branch_id'].nunique()}")
print(f"Unique products: {df_inventory['product_id'].nunique()}")

print("\nPreview:")
print(df_inventory.head(10))

# ==========================================
# 4. CALCULATE AVERAGE WEEKLY DEMAND
# ==========================================

# Calculate total units sold per product per branch
df_demand = (
    df_sales
    .groupby(["branch_id", "product_id"], as_index=False)
    .agg(total_units_sold=("quantity", "sum"))
)

# Calculate the number of weeks covered by the dataset
coverage_days = (end_date - start_date).days
coverage_weeks = coverage_days / 7

# Calculate average weekly demand
df_demand["avg_weekly_demand"] = (
    df_demand["total_units_sold"] / coverage_weeks
).round(2)

# Merge demand information into inventory structure
df_inventory = df_inventory.merge(
    df_demand[
        ["branch_id", "product_id", "total_units_sold", "avg_weekly_demand"]
    ],
    on=["branch_id", "product_id"],
    how="left"
)

# Handle product-branch combinations with no recorded sales
df_inventory["total_units_sold"] = (
    df_inventory["total_units_sold"].fillna(0).astype(int)
)

df_inventory["avg_weekly_demand"] = (
    df_inventory["avg_weekly_demand"].fillna(0)
)

# Calculate reorder level
# Minimum threshold: 3 units
df_inventory["reorder_level"] = np.maximum(
    3,
    np.ceil(df_inventory["avg_weekly_demand"] * 1.5)
).astype(int)

print("\nPRODUCT DEMAND CALCULATION")
print("=" * 40)

print(f"Product-branch combinations: {len(df_demand):,}")
print(f"Coverage weeks: {coverage_weeks:.2f}")

print("\nAverage weekly demand statistics:")
print(
    df_demand["avg_weekly_demand"].describe().round(2)
)

print("\nReorder level statistics:")
print(
    df_inventory["reorder_level"].describe().round(2)
)

print("\nSample inventory records:")
print(
    df_inventory[
        [
            "branch_id",
            "product_id",
            "total_units_sold",
            "avg_weekly_demand",
            "reorder_level"
        ]
    ].drop_duplicates(
        subset=["branch_id", "product_id"]
    ).head(10)
)

# ==========================================
# 5. GENERATE INVENTORY QUANTITIES
# ==========================================

# Start with a random stock coverage of 2–6 weeks
stock_coverage = rng.uniform(
    2,
    6,
    size=len(df_inventory)
)

# Generate normal stock levels based on weekly demand
df_inventory["quantity_on_hand"] = np.ceil(
    df_inventory["avg_weekly_demand"] * stock_coverage
).astype(int)

# Add small random fluctuations
stock_variation = rng.normal(
    loc=1.0,
    scale=0.20,
    size=len(df_inventory)
)

df_inventory["quantity_on_hand"] = np.maximum(
    0,
    np.round(
        df_inventory["quantity_on_hand"] * stock_variation
    )
).astype(int)


# ------------------------------------------
# STOCKOUT SCENARIO
# ------------------------------------------

# Selected products with recurring stock problems
stockout_products = [
    "PRD008",
    "PRD020",
    "PRD035",
    "PRD052",
    "PRD077",
    "PRD089",
    "PRD103",
    "PRD115"
]

stockout_mask = (
    (df_inventory["branch_id"] == "BR003")
    & (df_inventory["product_id"].isin(stockout_products))
)

# Randomly create stockout periods
stockout_events = (
    stockout_mask
    & (rng.random(len(df_inventory)) < 0.30)
)

df_inventory.loc[
    stockout_events,
    "quantity_on_hand"
] = 0

# Remaining selected records experience low stock
low_stock_events = stockout_mask & ~stockout_events

low_stock_factors = rng.uniform(
    0.20,
    0.90,
    size=low_stock_events.sum()
)

df_inventory.loc[
    low_stock_events,
    "quantity_on_hand"
] = np.floor(
    df_inventory.loc[
        low_stock_events,
        "reorder_level"
    ].to_numpy() * low_stock_factors
).astype(int)


# ------------------------------------------
# OVERSTOCK SCENARIO
# ------------------------------------------

# Selected products with unusually high inventory
overstock_products = [
    "PRD005",
    "PRD018",
    "PRD029",
    "PRD044",
    "PRD061",
    "PRD074",
    "PRD092",
    "PRD110"
]

overstock_mask = (
    (df_inventory["branch_id"] == "BR006")
    & (df_inventory["product_id"].isin(overstock_products))
)

overstock_factors = rng.uniform(
    4,
    8,
    size=overstock_mask.sum()
)

df_inventory.loc[
    overstock_mask,
    "quantity_on_hand"
] = np.ceil(
    df_inventory.loc[
        overstock_mask,
        "reorder_level"
    ].to_numpy() * overstock_factors
).astype(int)


print("\nINVENTORY QUANTITIES GENERATED")
print("=" * 40)

print(
    df_inventory["quantity_on_hand"].describe().round(2)
)

print("\nStock condition counts:")
print(
    pd.Series({
        "Stockout": (
            df_inventory["quantity_on_hand"] == 0
        ).sum(),

        "Low Stock": (
            (df_inventory["quantity_on_hand"] > 0)
            & (
                df_inventory["quantity_on_hand"]
                < df_inventory["reorder_level"]
            )
        ).sum(),

        "Normal Stock": (
            df_inventory["quantity_on_hand"]
            >= df_inventory["reorder_level"]
        ).sum()
    })
)

print("\nScenario records:")
print(f"Stockout scenario records: {stockout_mask.sum():,}")
print(f"Overstock scenario records: {overstock_mask.sum():,}")

# ==========================================
# 6. FINALIZE INVENTORY DATASET
# ==========================================

# Generate unique inventory IDs
df_inventory.insert(
    0,
    "inventory_id",
    [
        f"INV{i:07d}"
        for i in range(1, len(df_inventory) + 1)
    ]
)

# Keep only the required fact table columns
df_inventory = df_inventory[
    [
        "inventory_id",
        "date_id",
        "branch_id",
        "product_id",
        "quantity_on_hand",
        "reorder_level"
    ]
]

# Save inventory dataset
output_path = (
    config.RAW_DATA_DIR / "fact_inventory.csv"
)

df_inventory.to_csv(
    output_path,
    index=False
)

print("\nINVENTORY DATASET SAVED")
print("=" * 40)

print(f"Records: {len(df_inventory):,}")
print(f"Columns: {len(df_inventory.columns)}")
print(f"File: {output_path}")

print("\nFinal columns:")
print(df_inventory.columns.tolist())

print("\nDataset preview:")
print(df_inventory.head(10))