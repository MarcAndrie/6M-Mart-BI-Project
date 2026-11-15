# 6M Mart — Business Requirements

## 1. Project Overview

This project aims to develop a Business Intelligence solution for 6M Mart, a fictional Philippine supermarket chain operating eight branches.

The solution will analyze sales performance, branch operations, product profitability, promotional effectiveness, and inventory availability.

## 2. Business Objectives

1. Monitor overall sales and profitability.
2. Evaluate individual branch performance.
3. Identify high-performing and underperforming products.
4. Assess promotional effectiveness.
5. Monitor inventory availability and stockout risks.
6. Identify business trends and improvement opportunities.

## 3. Analytical Areas

### A. Sales Performance
- Total gross sales and net sales.
- Monthly and yearly sales trends.
- Total orders and units sold.
- Average order value.
- Sales growth and decline.

### B. Branch Performance
- Revenue by branch.
- Gross profit by branch.
- Branch sales growth.
- Branch performance comparison.
- Identification of underperforming branches.

### C. Product Performance
- Revenue by product.
- Gross profit by product.
- Product category performance.
- Units sold by product.
- Product profitability comparison.

### D. Promotional Effectiveness
- Revenue generated from promotional sales.
- Sales volume during promotional periods.
- Discount amounts.
- Profitability of promoted products.
- Comparison against appropriate non-promotional baselines.

### E. Inventory Performance
- Inventory availability.
- Stockout frequency.
- Low-stock products.
- Overstocked products.
- Inventory differences across branches.

### F. Business Trends and Opportunities
- Declining branch performance.
- Seasonal sales patterns.
- Product growth opportunities.
- Areas requiring management intervention.

## 4. Key Performance Indicators

| KPI | Calculation |
|---|---|
| Gross Sales | Sales before discounts and returns |
| Net Sales | Gross Sales - Discounts - Returns |
| Total Orders | Distinct completed transaction IDs |
| Units Sold | Sold quantities less returned quantities |
| Average Order Value | Net Sales / Total Orders |
| COGS | Cost of goods sold |
| Gross Profit | Net Sales - COGS |
| Gross Profit Margin | Gross Profit / Net Sales × 100 |
| Discount Amount | Total discounts |
| Return Rate | Returned Units / Sold Units × 100 |
| Stockout Rate | Stockout product-branch periods / Monitored product-branch periods × 100 |

## 5. Data Requirements

The project requires the following datasets:

- Sales Transactions
- Product Master Data
- Branch Master Data
- Inventory Records
- Promotional Campaigns
- Supplier Information

## 6. Expected Deliverables

1. Data Quality Report
2. PostgreSQL Database and SQL Analytics Repository
3. Interactive Power BI Dashboard
4. Business Insights and Recommendations Report

## 7. Data Scope

- Business: 6M Mart
- Branches: 8
- Coverage: January 2024 – December 2025
- Currency: PHP
- Data: Synthetic / Simulated

## 8. Project Limitations

All datasets and business findings are simulated for educational and portfolio demonstration purposes. Promotional effectiveness will be evaluated using observational comparisons and should not automatically be interpreted as causal impact.