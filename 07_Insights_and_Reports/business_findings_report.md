# 6M Mart – Business Findings & Recommendations Report

**Project:** Retail Intelligence & Performance Analytics  
**Analysis Period:** January 1, 2024 – December 31, 2025  
**Currency:** Philippine Peso (PHP)  
**Data Classification:** Synthetic / Simulated Data

---

## 1. Executive Summary

This report presents the findings of an end-to-end Business Intelligence analysis of 6M Mart, a fictional supermarket chain operating eight branches across Cavite and Metro Manila.

The analysis covers sales performance, branch performance, product profitability, promotional effectiveness, inventory conditions, and product returns.

Across the two-year period, the business generated approximately **₱37.52 million in net sales**, with a gross profit of **₱10.59 million** and an overall gross profit margin of **28.21%**.

Although overall sales increased slightly in 2025, performance varied considerably between branches and products. Some branches experienced declining sales and profitability, while inventory analysis identified potential replenishment and stock redistribution opportunities.

## 2. Overall Business Performance

| KPI | Result |
|---|---:|
| Gross Sales | ₱38,883,413.57 |
| Total Discounts | ₱771,157.80 |
| Total Refunds | ₱588,203.66 |
| Net Sales | ₱37,524,052.11 |
| Total Orders | 40,050 |
| Net Units Sold | 244,224 |
| Average Order Value | ₱936.93 |
| Cost of Goods Sold | ₱26,937,727.87 |
| Gross Profit | ₱10,586,324.24 |
| Gross Profit Margin | 28.21% |
| Return Rate | 1.54% |

### Key Findings

- Net sales increased from ₱18.74 million in 2024 to ₱18.78 million in 2025, representing only **0.23% year-over-year growth**.
- December was the strongest sales month in both years, while February was the weakest.
- January 2025 experienced a 31.40% month-over-month decline following the December seasonal peak.

**Business Implication:** Overall sales remained relatively stable, but growth was limited. Management should investigate the differences in branch performance and product profitability rather than relying solely on company-wide revenue.

## 3. Branch Performance

### Key Findings

Three branches experienced year-over-year sales declines in 2025:

| Branch | Sales Growth |
|---|---:|
| 6M Bacoor | -10.17% |
| 6M Silang | -5.35% |
| 6M General Trias | -4.17% |

Meanwhile, 6M Las Piñas recorded the strongest growth at **13.72%**, increasing net sales by approximately ₱305,975.

Bacoor also experienced a 12.80% decline in orders, indicating that its sales decline was accompanied by fewer transactions.

### Business Recommendations

- Investigate the decline in customer transactions at Bacoor.
- Review sales trends, product availability, and branch-level operating conditions in Silang and General Trias.
- Study the performance of Las Piñas to identify practices that may be useful in other branches.
- Monitor order volume and average order value together to understand the factors behind sales changes.

## 4. Product and Category Performance

### Key Findings

- Groceries generated the largest category sales contribution at **41.95%**.
- Personal Care achieved the highest category gross profit margin at **30.17%**.
- Cooking Oil 1L was the highest-selling product, generating approximately ₱4.36 million in net sales.
- Facial Cleanser 100ml recorded the strongest product sales growth at 30.19%.
- Bath Soap 135g experienced the largest product sales decline at 30.39%.

The analysis also identified 29 high-revenue products with declining gross profit.

Chocolate Powder recorded the largest profit decline among these products, at approximately ₱21,783.

### Business Recommendations

- Review the cost and pricing structure of products with declining profitability.
- Investigate products generating substantial revenue but relatively low margins.
- Evaluate whether declining products require pricing adjustments, promotional changes, or further investigation.
- Continue monitoring Personal Care products because of their comparatively strong category margin.

## 5. Promotional Effectiveness

### Key Findings

Promoted sales recorded a gross profit margin of **21.53%**, compared with **29.63%** for non-promoted sales.

This represents an 8.10 percentage-point difference.

PROM011 Summer Sale was identified in the SQL analysis as a leading promotion by net sales and gross profit.

### Business Recommendations

- Review discount levels and campaign profitability before extending promotions.
- Evaluate promotional performance using both revenue and gross profit.
- Identify whether promotions are supporting incremental sales or primarily reducing margins.
- Monitor individual promotion campaigns separately rather than combining campaigns with similar names.

**Interpretation Limitation:** The margin difference is descriptive and does not establish that promotions caused lower profitability. Transactions may contain both promoted and non-promoted sales lines. Individual promotion figures also require final reconciliation between the Power BI model and SQL analysis.

## 6. Inventory Analysis

### Key Findings

The inventory dataset contains 101,760 weekly inventory snapshots.

| Inventory KPI | Result |
|---|---:|
| Total Inventory Records | 101,760 |
| Stockout Records | 327 |
| Stockout Rate | 0.32% |
| Low Stock Records | 9,376 |
| Low Stock Rate | 9.22% |

6M Bacoor recorded the highest stockout rate at approximately **2.52%**.

6M Las Piñas had the highest overstock rate at **26.01%**.

Bell Pepper 500g, Laundry Bar Soap, and Dishwashing Liquid were among the products with the most frequent stockout observations.

### Business Recommendations

- Review replenishment practices and stock availability in Bacoor.
- Investigate products that repeatedly experience stockouts.
- Evaluate possible stock redistribution opportunities between branches.
- Review persistent overstock conditions in Las Piñas to reduce unnecessary inventory holding.

**Interpretation Limitation:** Inventory records represent weekly snapshots. They cannot establish the exact duration of stockouts or quantify sales that may have been lost because of unavailable products.

## 7. Returns and Refunds Analysis

### Key Findings

The business recorded 2,469 return events involving 3,818 returned units.

The overall return rate was **1.54%**.

The annual return rates were relatively stable:

| Year | Returned Units | Refund Amount | Return Rate |
|---|---:|---:|---:|
| 2024 | 1,901 | ₱289,717.35 | 1.53% |
| 2025 | 1,917 | ₱298,486.31 | 1.54% |

Conditioner 340ml, Evaporated Milk 370ml, and Milk Tea Drink 500ml were among the products with the highest return rates among products with at least 100 units sold.

### Business Recommendations

- Monitor products with consistently high return rates.
- Investigate product quality, packaging, and handling conditions where appropriate.
- Review refund exposure alongside return frequency.
- Consider collecting return reasons in future business systems to support more detailed root-cause analysis.

**Interpretation Limitation:** Return reasons were not included in the synthetic dataset. Late-period return rates may also be affected by the shorter time available for returns to occur.

## 8. Priority Business Opportunities

Based on the findings, the following areas deserve management attention:

| Priority | Opportunity | Suggested Action |
|---|---|---|
| High | Bacoor sales decline | Investigate declining orders and branch performance |
| High | Inventory availability | Review recurring stockouts and replenishment |
| High | Product profitability | Investigate high-revenue products with declining profit |
| Medium | Promotional margins | Review discount structures and campaign performance |
| Medium | Overstock | Evaluate stock redistribution and purchasing decisions |
| Medium | Product returns | Monitor products with elevated return rates |

## 9. Analytical Limitations

The following limitations should be considered when interpreting the findings:

1. All records are synthetically generated and do not represent actual business operations.
2. The analysis is descriptive and does not establish causation.
3. Inventory data consists of weekly snapshots rather than continuous inventory tracking.
4. Return reasons and customer-level information are not available.
5. Recent return cohorts may be affected by incomplete observation periods.
6. Promotional comparisons may involve transactions containing multiple promotion types.
7. Gross profit does not account for operating expenses and should not be interpreted as net income.

## 10. Conclusion

The analysis demonstrates how an integrated Business Intelligence workflow can support retail performance monitoring and business decision-making.

Although 6M Mart achieved relatively stable overall sales in 2025, the findings reveal opportunities to improve branch performance, product profitability, promotional efficiency, inventory availability, and return monitoring.

The project demonstrates the practical application of Python, PostgreSQL, SQL, Power BI, and DAX in transforming raw datasets into structured analysis and actionable business recommendations.