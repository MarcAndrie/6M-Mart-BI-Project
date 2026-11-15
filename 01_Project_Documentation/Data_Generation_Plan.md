# 6M Mart — Synthetic Data Generation Plan

## 1. Objective

Generate realistic synthetic datasets representing the business operations of 6M Mart from January 1, 2024 to December 31, 2025.

The datasets will support sales analysis, branch comparisons, product profitability, promotional effectiveness, and inventory monitoring.

## 2. Planned Dataset Volumes

| Dataset | Target Records |
|---|---:|
| Products | 120 |
| Branches | 8 |
| Suppliers | 15 |
| Promotions | 15 |
| Calendar | 731 |
| Sales | 100,000–150,000 line items |
| Inventory | Approximately 100,000 |
| Returns | Approximately 1–3% of sales line items |

## 3. Business Scenarios

The generator will simulate:

1. Increased sales during November and December.
2. Sustained sales decline in one branch.
3. Gradual growth in another branch.
4. Different product popularity levels.
5. Seasonal product demand.
6. Promotional campaigns affecting sales volume and margins.
7. High-revenue products with relatively low profitability.
8. Inventory shortages in selected products.
9. Excess inventory in selected products.
10. Occasional product returns.

All scenarios will be documented and validated through independent analysis.

## 4. Dataset Structure

### Master Data
- dim_products
- dim_branches
- dim_suppliers
- dim_promotions
- dim_date

### Transactional Data
- fact_sales
- fact_inventory
- fact_returns

## 5. Financial Calculation Rules

Gross Sales = Quantity × Unit Price

Net Sales Before Returns = Gross Sales − Discount Amount

Net Revenue = Net Sales Before Returns − Refund Amount

Net COGS = (Quantity Sold − Returned Quantity) × Unit Cost

Gross Profit = Net Revenue − Net COGS

Gross Profit Margin = Gross Profit / Net Revenue × 100

## 6. Data Integrity Requirements

- Primary keys must be unique.
- Foreign keys must reference valid records.
- Sales transactions must have valid dates, branches, and products.
- Returned quantities cannot exceed original sold quantities.
- Discounts cannot exceed gross sales.
- Inventory quantities cannot be negative.
- Product costs and selling prices must be positive.
- Historical sales costs and prices must be preserved.
- Transaction IDs must correctly identify customer receipts.

## 7. Python Scripts

| Script | Purpose |
|---|---|
| config.py | Configuration |
| generate_master_data.py | Master data generation |
| generate_sales.py | Sales generation |
| generate_inventory.py | Inventory generation |
| generate_returns.py | Returns generation |
| validate_data.py | Data validation |
| main.py | Main execution script |

## 8. Python Libraries

- Pandas
- NumPy
- Python Standard Library

## 9. Output Format

Datasets will initially be exported as CSV files and stored in the project's raw data directory.

Original generated data will remain unchanged. Any cleaned datasets will be stored separately.

## 10. Important Limitations

The datasets are synthetic and designed for portfolio demonstration.

Promotional effectiveness will be assessed through observational comparisons, not automatically interpreted as causal impact.

Weekly inventory snapshots provide periodic stock visibility and cannot establish the exact timing of every stockout.