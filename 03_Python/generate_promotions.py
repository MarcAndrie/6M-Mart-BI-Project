
import pandas as pd
import config

# ==========================================
# 1. DEFINE PROMOTION MASTER DATA
# ==========================================

promotions = [
    {
        "promotion_id": "PROM001",
        "promotion_name": "New Year Savings",
        "discount_type": "Percentage",
        "start_date": "2024-01-01",
        "end_date": "2024-01-15"
    },
    {
        "promotion_id": "PROM002",
        "promotion_name": "Valentine's Special",
        "discount_type": "Percentage",
        "start_date": "2024-02-10",
        "end_date": "2024-02-18"
    },
    {
        "promotion_id": "PROM003",
        "promotion_name": "Summer Sale",
        "discount_type": "Percentage",
        "start_date": "2024-04-01",
        "end_date": "2024-04-30"
    },
    {
        "promotion_id": "PROM004",
        "promotion_name": "Mid-Year Mega Sale",
        "discount_type": "Percentage",
        "start_date": "2024-06-15",
        "end_date": "2024-06-30"
    },
    {
        "promotion_id": "PROM005",
        "promotion_name": "Back to School Deals",
        "discount_type": "Fixed Amount",
        "start_date": "2024-06-01",
        "end_date": "2024-06-30"
    },
    {
        "promotion_id": "PROM006",
        "promotion_name": "9.9 Super Sale",
        "discount_type": "Percentage",
        "start_date": "2024-09-09",
        "end_date": "2024-09-11"
    },
    {
        "promotion_id": "PROM007",
        "promotion_name": "11.11 Mega Sale",
        "discount_type": "Percentage",
        "start_date": "2024-11-10",
        "end_date": "2024-11-12"
    },
    {
        "promotion_id": "PROM008",
        "promotion_name": "Christmas Countdown",
        "discount_type": "Percentage",
        "start_date": "2024-12-15",
        "end_date": "2024-12-31"
    },
    {
        "promotion_id": "PROM009",
        "promotion_name": "New Year Savings",
        "discount_type": "Percentage",
        "start_date": "2025-01-01",
        "end_date": "2025-01-15"
    },
    {
        "promotion_id": "PROM010",
        "promotion_name": "Valentine's Special",
        "discount_type": "Percentage",
        "start_date": "2025-02-10",
        "end_date": "2025-02-18"
    },
    {
        "promotion_id": "PROM011",
        "promotion_name": "Summer Sale",
        "discount_type": "Percentage",
        "start_date": "2025-04-01",
        "end_date": "2025-04-30"
    },
    {
        "promotion_id": "PROM012",
        "promotion_name": "Mid-Year Mega Sale",
        "discount_type": "Percentage",
        "start_date": "2025-06-15",
        "end_date": "2025-06-30"
    },
    {
        "promotion_id": "PROM013",
        "promotion_name": "9.9 Super Sale",
        "discount_type": "Percentage",
        "start_date": "2025-09-09",
        "end_date": "2025-09-11"
    },
    {
        "promotion_id": "PROM014",
        "promotion_name": "11.11 Mega Sale",
        "discount_type": "Percentage",
        "start_date": "2025-11-10",
        "end_date": "2025-11-12"
    },
    {
        "promotion_id": "PROM015",
        "promotion_name": "Christmas Countdown",
        "discount_type": "Percentage",
        "start_date": "2025-12-15",
        "end_date": "2025-12-31"
    }
]

# ==========================================
# 2. CREATE PROMOTION DATAFRAME
# ==========================================

df_promotions = pd.DataFrame(promotions)

# ==========================================
# 2.1 DEFINE PROMOTION DISCOUNT VALUES
# ==========================================

discount_values = {
    "PROM001": 10,
    "PROM002": 10,
    "PROM003": 10,
    "PROM004": 15,
    "PROM005": 10,
    "PROM006": 10,
    "PROM007": 15,
    "PROM008": 10,
    "PROM009": 10,
    "PROM010": 10,
    "PROM011": 10,
    "PROM012": 15,
    "PROM013": 10,
    "PROM014": 15,
    "PROM015": 10
}

df_promotions["discount_value"] = (
    df_promotions["promotion_id"].map(discount_values)
)

# Convert promotion dates into proper date values.
df_promotions["start_date"] = pd.to_datetime(
    df_promotions["start_date"]
)

df_promotions["end_date"] = pd.to_datetime(
    df_promotions["end_date"]
)

# ==========================================
# 3. SAVE PROMOTION DATASET
# ==========================================

output_path = config.RAW_DATA_DIR / "dim_promotions.csv"

df_promotions.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 4. DISPLAY GENERATION SUMMARY
# ==========================================

print("Promotion dataset generated successfully!")
print(f"Total promotions: {len(df_promotions)}")

print("\nPromotion Preview:")
print(df_promotions)

print(f"\nSaved to: {output_path}")
