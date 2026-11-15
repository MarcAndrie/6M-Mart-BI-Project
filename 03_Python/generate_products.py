
import pandas as pd
import numpy as np
import config

# ==========================================
# 1. REPRODUCIBLE RANDOM GENERATOR
# ==========================================

rng = np.random.default_rng(config.RANDOM_SEED)

# ==========================================
# 2. PRODUCT CATALOG
# ==========================================

product_catalog = {
    "Groceries": [
        "Premium Rice 5kg", "Regular Rice 5kg", "Jasmine Rice 2kg",
        "Brown Rice 2kg", "All-Purpose Flour 1kg",
        "White Sugar 1kg", "Brown Sugar 1kg", "Cooking Oil 1L",
        "Soy Sauce 500ml", "Vinegar 500ml", "Fish Sauce 500ml",
        "Canned Tuna", "Canned Sardines", "Instant Noodles",
        "Spaghetti Pasta 500g", "Tomato Sauce 500g",
        "Peanut Butter 350g", "Oatmeal 500g", "Coffee 200g",
        "Chocolate Powder 300g"
    ],

    "Beverages": [
        "Bottled Water 500ml", "Bottled Water 1L",
        "Cola 1.5L", "Cola 500ml", "Lemon Soda 1.5L",
        "Orange Juice 1L", "Apple Juice 1L", "Iced Tea 500ml",
        "Energy Drink 250ml", "Sports Drink 500ml",
        "Instant Coffee Drink", "Powdered Juice 500g",
        "Green Tea 500ml", "Milk Tea Drink 500ml",
        "Chocolate Drink 250ml", "Mango Juice 1L",
        "Coconut Water 500ml", "Root Beer 1.5L",
        "Sparkling Water 500ml", "Lemonade 1L"
    ],

    "Dairy": [
        "Fresh Milk 1L", "Fresh Milk 500ml", "Chocolate Milk 1L",
        "Condensed Milk 390g", "Evaporated Milk 370ml",
        "Cheddar Cheese 165g", "Processed Cheese 200g",
        "Butter 225g", "Margarine 250g", "Plain Yogurt 500g",
        "Strawberry Yogurt 500g", "Greek Yogurt 400g",
        "Vanilla Ice Cream 1L", "Chocolate Ice Cream 1L",
        "Whipped Cream 250ml", "Cream Cheese 200g",
        "UHT Milk 1L", "Powdered Milk 300g",
        "Sour Cream 250g", "Milk Powder Sachet"
    ],

    "Fresh Produce": [
        "Banana 1kg", "Apple 1kg", "Orange 1kg", "Mango 1kg",
        "Papaya 1kg", "Watermelon 1kg", "Pineapple 1pc",
        "Tomato 1kg", "Potato 1kg", "Onion 1kg",
        "Garlic 250g", "Carrot 1kg", "Cabbage 1pc",
        "Eggplant 1kg", "Cucumber 1kg", "Lettuce 1pc",
        "Bell Pepper 500g", "Calamansi 500g",
        "Sweet Potato 1kg", "Ginger 250g"
    ],

    "Personal Care": [
        "Bath Soap 135g", "Shampoo 340ml", "Conditioner 340ml",
        "Toothpaste 150g", "Toothbrush Medium",
        "Mouthwash 500ml", "Facial Cleanser 100ml",
        "Body Lotion 400ml", "Deodorant Roll-On",
        "Deodorant Spray", "Facial Tissue Pack",
        "Cotton Buds 200pcs", "Feminine Wash 150ml",
        "Hand Sanitizer 250ml", "Sunscreen 100ml",
        "Baby Powder 200g", "Hair Gel 150g",
        "Disposable Razor", "Dental Floss 50m",
        "Liquid Hand Soap 500ml"
    ],

    "Household Essentials": [
        "Laundry Detergent 1kg", "Fabric Conditioner 1L",
        "Dishwashing Liquid 500ml", "Bleach 1L",
        "Floor Cleaner 1L", "Glass Cleaner 500ml",
        "Toilet Cleaner 500ml", "Garbage Bags 20pcs",
        "Paper Towels 2 Rolls", "Toilet Tissue 4 Rolls",
        "Sponge Pack 3pcs", "Scrub Pad 3pcs",
        "Air Freshener 300ml", "Insect Spray 500ml",
        "Laundry Bar Soap", "Cloth Hanger 5pcs",
        "Food Storage Container", "Aluminum Foil 10m",
        "Plastic Wrap 30m", "Microfiber Cleaning Cloth"
    ]
}

# ==========================================
# 3. CATEGORY PRICE RANGES
# ==========================================

price_ranges = {
    "Groceries": (20, 350),
    "Beverages": (15, 180),
    "Dairy": (35, 280),
    "Fresh Produce": (15, 200),
    "Personal Care": (25, 350),
    "Household Essentials": (20, 300)
}

# ==========================================
# 4. SUPPLIER ASSIGNMENT
# ==========================================

df_suppliers = pd.read_csv(
    config.RAW_DATA_DIR / "dim_suppliers.csv"
)

# ==========================================
# 5. GENERATE PRODUCT RECORDS
# ==========================================

products = []

for category, product_names in product_catalog.items():

    category_suppliers = df_suppliers[
        df_suppliers["supplier_category"] == category
    ]["supplier_id"].tolist()

    min_price, max_price = price_ranges[category]

    for product_name in product_names:

        selling_price = round(
            float(rng.uniform(min_price, max_price)),
            2
        )

        # Unit cost is 55% to 85% of selling price.
        cost_ratio = rng.uniform(0.55, 0.85)

        unit_cost = round(
            selling_price * cost_ratio,
            2
        )

        supplier_id = rng.choice(category_suppliers)

        products.append({
            "product_id": f"PRD{len(products) + 1:03d}",
            "product_name": product_name,
            "category": category,
            "selling_price": selling_price,
            "unit_cost": unit_cost,
            "supplier_id": supplier_id
        })

# ==========================================
# 6. CREATE PRODUCT DATAFRAME
# ==========================================

df_products = pd.DataFrame(products)

# ==========================================
# 7. SAVE PRODUCT DATASET
# ==========================================

output_path = config.RAW_DATA_DIR / "dim_products.csv"

df_products.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 8. DISPLAY GENERATION SUMMARY
# ==========================================

print("Product dataset generated successfully!")
print(f"Total products: {len(df_products)}")

print("\nProducts per category:")
print(df_products["category"].value_counts())

print("\nProduct Preview:")
print(df_products.head(10))

print(f"\nSaved to: {output_path}")
