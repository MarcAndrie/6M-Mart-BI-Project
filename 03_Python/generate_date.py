
import pandas as pd
import config

# ==========================================
# 1. GENERATE CALENDAR DATES
# ==========================================

date_range = pd.date_range(
    start=config.START_DATE,
    end=config.END_DATE,
    freq="D"
)

# ==========================================
# 2. CREATE DATE DATAFRAME
# ==========================================

df_dates = pd.DataFrame({
    "full_date": date_range
})

# ==========================================
# 3. CREATE DATE ATTRIBUTES
# ==========================================

df_dates["date_id"] = df_dates["full_date"].dt.strftime("%Y%m%d").astype(int)

df_dates["day"] = df_dates["full_date"].dt.day

df_dates["month"] = df_dates["full_date"].dt.month

df_dates["month_name"] = df_dates["full_date"].dt.month_name()

df_dates["quarter"] = "Q" + df_dates["full_date"].dt.quarter.astype(str)

df_dates["year"] = df_dates["full_date"].dt.year

df_dates["day_of_week"] = df_dates["full_date"].dt.day_name()

# ==========================================
# 4. ARRANGE COLUMN ORDER
# ==========================================

df_dates = df_dates[
    [
        "date_id",
        "full_date",
        "day",
        "month",
        "month_name",
        "quarter",
        "year",
        "day_of_week"
    ]
]

# ==========================================
# 5. SAVE DATE DATASET
# ==========================================

output_path = config.RAW_DATA_DIR / "dim_date.csv"

df_dates.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 6. DISPLAY GENERATION SUMMARY
# ==========================================

print("Date dataset generated successfully!")
print(f"Total calendar days: {len(df_dates)}")

print("\nDate range:")
print(df_dates["full_date"].min(), "to", df_dates["full_date"].max())

print("\nDate Preview:")
print(df_dates.head())

print("\nLeap year check:")
print(
    df_dates[
        (df_dates["month"] == 2) &
        (df_dates["day"] == 29)
    ]
)

print(f"\nSaved to: {output_path}")
