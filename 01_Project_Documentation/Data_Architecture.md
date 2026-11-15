# 6M Mart — Data Architecture & Database Design

## 1. Architecture Overview

The project will use a relational database with a star-schema-inspired analytical model.

The database will separate transactional business events from descriptive business information to support efficient querying and reporting.

## 2. Dimension Tables

### dim_products
- product_id (Primary Key)
- product_name
- category
- selling_price
- unit_cost
- supplier_id (Foreign Key)

### dim_branches
- branch_id (Primary Key)
- branch_name
- city
- region
- branch_type

### dim_date
- date_id (Primary Key)
- full_date
- day
- month
- month_name
- quarter
- year
- day_of_week

### dim_promotions
- promotion_id (Primary Key)
- promotion_name
- discount_type
- start_date
- end_date

### dim_suppliers
- supplier_id (Primary Key)
- supplier_name
- supplier_category

## 3. Fact Tables

### fact_sales

**Grain:** One row per product line within a customer transaction.

- sales_line_id (Primary Key)
- transaction_id
- date_id (Foreign Key)
- branch_id (Foreign Key)
- product_id (Foreign Key)
- promotion_id (Foreign Key, nullable)
- quantity
- unit_price
- unit_cost
- discount_amount

### fact_inventory

**Grain:** One row per product, per branch, per inventory snapshot date.

- inventory_id (Primary Key)
- date_id (Foreign Key)
- branch_id (Foreign Key)
- product_id (Foreign Key)
- quantity_on_hand
- reorder_level

Inventory snapshots will initially be generated weekly.

### fact_returns

**Grain:** One row per returned product line event.

- return_id (Primary Key)
- original_sales_line_id (Foreign Key)
- date_id (Foreign Key)
- branch_id (Foreign Key)
- product_id (Foreign Key)
- returned_quantity
- refund_amount

## 4. Database Relationships

- dim_products → fact_sales
- dim_products → fact_inventory
- dim_products → fact_returns
- dim_branches → fact_sales
- dim_branches → fact_inventory
- dim_branches → fact_returns
- dim_date → fact_sales
- dim_date → fact_inventory
- dim_date → fact_returns
- dim_promotions → fact_sales
- dim_suppliers → dim_products
- fact_sales → fact_returns

All dimension-to-fact relationships will follow a one-to-many structure.

## 5. Data Grain

| Table | Grain |
|---|---|
| fact_sales | One product line per transaction |
| fact_inventory | One product per branch per snapshot date |
| fact_returns | One returned product line event |
| dim_products | One record per product |
| dim_branches | One record per branch |
| dim_date | One record per calendar date |
| dim_promotions | One record per promotion |
| dim_suppliers | One record per supplier |

## 6. Analytical Considerations

- Transaction counts must use distinct transaction IDs.
- Historical unit costs must be preserved in sales records.
- Returns must be accounted for when calculating net sales.
- Inventory snapshots must be evaluated at the correct product, branch, and date grain.
- Promotional performance must be evaluated against appropriate comparison periods.
- Relationships must avoid unintended many-to-many joins and double counting.

## 7. Planned Technology

- Database: PostgreSQL
- Data preparation: Python and Excel
- Visualization: Microsoft Power BI
- Version control: GitHub

## 8. Data Modeling Objective

The database design will provide a consistent foundation for transactional analysis, profitability measurement, branch comparisons, promotional evaluation, and inventory monitoring.