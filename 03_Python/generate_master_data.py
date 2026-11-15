
import pandas as pd
import config

# ==========================================
# 1. DEFINE BRANCH MASTER DATA
# ==========================================

branches = [
    {
        "branch_id": "BR001",
        "branch_name": "6M Dasmariñas",
        "city": "Dasmariñas",
        "region": "Cavite",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR002",
        "branch_name": "6M Imus",
        "city": "Imus",
        "region": "Cavite",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR003",
        "branch_name": "6M Bacoor",
        "city": "Bacoor",
        "region": "Cavite",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR004",
        "branch_name": "6M General Trias",
        "city": "General Trias",
        "region": "Cavite",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR005",
        "branch_name": "6M Silang",
        "city": "Silang",
        "region": "Cavite",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR006",
        "branch_name": "6M Las Piñas",
        "city": "Las Piñas",
        "region": "Metro Manila",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR007",
        "branch_name": "6M Parañaque",
        "city": "Parañaque",
        "region": "Metro Manila",
        "branch_type": "Supermarket"
    },
    {
        "branch_id": "BR008",
        "branch_name": "6M Muntinlupa",
        "city": "Muntinlupa",
        "region": "Metro Manila",
        "branch_type": "Supermarket"
    }
]

# ==========================================
# 2. CONVERT DATA INTO A DATAFRAME
# ==========================================

df_branches = pd.DataFrame(branches)

# ==========================================
# 3. SAVE DATASET AS CSV
# ==========================================

config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

output_path = config.RAW_DATA_DIR / "dim_branches.csv"

df_branches.to_csv(output_path, index=False, encoding="utf-8-sig")

# ==========================================
# 4. DISPLAY GENERATION SUMMARY
# ==========================================

print("Branch dataset generated successfully!")
print(f"Total branches: {len(df_branches)}")
print(f"Saved to: {output_path}")

print("\nBranch Preview:")
print(df_branches)


# ==========================================
# 5. DEFINE SUPPLIER MASTER DATA
# ==========================================

suppliers = [
    {"supplier_id": "SUP001", "supplier_name": "Luzon Grocery Distributors", "supplier_category": "Groceries"},
    {"supplier_id": "SUP002", "supplier_name": "Prime Food Trading", "supplier_category": "Groceries"},
    {"supplier_id": "SUP003", "supplier_name": "Metro Consumer Goods Supply", "supplier_category": "Groceries"},

    {"supplier_id": "SUP004", "supplier_name": "Refresh Beverage Trading", "supplier_category": "Beverages"},
    {"supplier_id": "SUP005", "supplier_name": "Golden Drinks Distribution", "supplier_category": "Beverages"},
    {"supplier_id": "SUP006", "supplier_name": "Pacific Beverage Supply", "supplier_category": "Beverages"},

    {"supplier_id": "SUP007", "supplier_name": "Fresh Dairy Products Supply", "supplier_category": "Dairy"},
    {"supplier_id": "SUP008", "supplier_name": "Milky Way Food Distributors", "supplier_category": "Dairy"},

    {"supplier_id": "SUP009", "supplier_name": "Green Harvest Trading", "supplier_category": "Fresh Produce"},
    {"supplier_id": "SUP010", "supplier_name": "Farm Fresh Distributors", "supplier_category": "Fresh Produce"},

    {"supplier_id": "SUP011", "supplier_name": "CarePlus Distribution", "supplier_category": "Personal Care"},
    {"supplier_id": "SUP012", "supplier_name": "Daily Essentials Trading", "supplier_category": "Personal Care"},

    {"supplier_id": "SUP013", "supplier_name": "Home Needs Wholesale", "supplier_category": "Household Essentials"},
    {"supplier_id": "SUP014", "supplier_name": "Reliable Household Supply", "supplier_category": "Household Essentials"},
    {"supplier_id": "SUP015", "supplier_name": "Practical Living Distributors", "supplier_category": "Household Essentials"}
]

# ==========================================
# 6. CONVERT SUPPLIERS INTO A DATAFRAME
# ==========================================

df_suppliers = pd.DataFrame(suppliers)

# ==========================================
# 7. SAVE SUPPLIER DATASET
# ==========================================

supplier_output_path = config.RAW_DATA_DIR / "dim_suppliers.csv"

df_suppliers.to_csv(
    supplier_output_path,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 8. DISPLAY SUPPLIER GENERATION SUMMARY
# ==========================================

print("\nSupplier dataset generated successfully!")
print(f"Total suppliers: {len(df_suppliers)}")
print(f"Saved to: {supplier_output_path}")

print("\nSupplier Preview:")
print(df_suppliers)


